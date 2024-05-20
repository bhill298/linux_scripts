#!/usr/bin/env python3
import sys

if len(sys.argv) != 3:
    print("Usage: %s <in_ll_file> <func_name:line_no_zero_based>" % sys.argv[0])
    sys.exit(1)

in_file = sys.argv[1]
in_function, in_line = sys.argv[2].split(':')
in_line = int(in_line, 0)

# line, actual_line_no (starting from 1)
lines = []
line_index = 0
current_line_no = 1
# [name] -> lines_index
fun_start_map = {}
with open(in_file, 'r') as f:
    for line in f:
        # trailing whitespace needs to be stripped, otherwise blank lines len will be > 0
        line = line.rstrip()
        # skip empty lines, comment lines, debug lines
        if len(line) > 0 and not line[0] == ';' and not line[0] == '!' and not "@llvm.dbg" in line:
            lines.append((line, current_line_no))
            # function definition
            if line.startswith("define") and '@' in line:
                fun_start_map[line[line.find('@')+1:line.find('(')].lower()] = line_index
            line_index += 1
        current_line_no += 1

if in_function not in fun_start_map:
    print("Could not find function name %s" % in_function)
    sys.exit(1)
line_index = fun_start_map[in_function.lower()] + 1 + in_line
if line_index > len(lines):
    print("Invalid line number %i" % in_line)
line, line_no = lines[line_index]
print("%i %s" % (line_no, line))
