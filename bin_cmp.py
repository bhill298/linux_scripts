#!/usr/bin/env python3
import argparse
import os
import sys

MAX_CHUNK_SIZE = 65536
NUM_CHARS_HEX_PREFIX = 2
NUM_CHARS_HEX_BYTE = 2
HEADER_COL1 = "offset"

def byte_to_string(byte):
    SYMBOLS = ('B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB')
    RATIO = 1024

    i = 0
    while i < len(SYMBOLS) - 1 and byte >= RATIO:
        byte /= RATIO
        i += 1
    return "%f %s" % (byte, SYMBOLS[i])

def hex_int_arg(arg):
    # argument function for argparse, returns an int form a string
    # the string should be formatted as a python string literal
    # (either no prefix or a 0x/0X, 0o/0O, 0b/0B prefix)
    try:
        arg = int(arg, 0)
    except ValueError:
        msg = ("%r is not a valid hex or integer number "
               "(the 0x prefix is required for hex)") % arg
        raise argparse.ArgumentTypeError(msg)
    if arg < 0:
        raise argparse.ArgumentTypeError("Cannot be less than 0")
    return arg

def chunk_size_arg(arg):
    try:
        arg = int(arg)
    except ValueError as err:
        raise argparse.ArgumentTypeError(err)
    if arg < -1 or arg == 0 or arg > MAX_CHUNK_SIZE:
        raise argparse.ArgumentTypeError("Enter an integer between [1, %i] or -1"
                                         % MAX_CHUNK_SIZE)
    return arg

def print_stats(bytes_read, differences):
    print("%s read" % byte_to_string(bytes_read))
    if bytes_read != 0:
        print("%s differences found (%s differ)" % (format(differences, ',d'),
                                                    byte_to_string(differences)))
        print("Similarity: %f%%" % ((1 - (differences / bytes_read)) * 100))

parser = argparse.ArgumentParser(description="Compare binary differences "
                                 "between 2 files, byte by byte.",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("file1", help="the first filename to compare")
parser.add_argument("file2", help="the second filename to compare")
parser.add_argument("-q", "--quiet", action="store_true",
                    help="don't print individual bytes that differ")
parser.add_argument("-s", "--chunksize", type=chunk_size_arg, default=256,
                    help="number of bytes to read at a time, -1 means read the "
                    "entire file at once, max is %i" % MAX_CHUNK_SIZE)
parser.add_argument("-b", "--bytes", type=int, default=4,
                    help="number of bytes to print address offset as")
parser.add_argument("-o", "--offset", type=hex_int_arg, default="0x0",
                    help="starting address to print offsets from")
parser.add_argument("-c", "--csv", action="store_true",
                    help="output in csv format")
args = parser.parse_args()

MAX_OFFSET = pow(2, 8 * args.bytes) - 1
HEADER_ADDR_DIFF = ((NUM_CHARS_HEX_PREFIX + args.bytes * NUM_CHARS_HEX_BYTE) - len(HEADER_COL1))
HEADER_PADDING = ' ' * HEADER_ADDR_DIFF
ADDR_PADDING = ' ' * -HEADER_ADDR_DIFF if HEADER_ADDR_DIFF < 0 else ''
F1_PADDING = ' ' * (len(args.file1) - (NUM_CHARS_HEX_PREFIX + NUM_CHARS_HEX_BYTE))
if args.csv:
    DIFF_FMT_STR = "0x%%0%ix,0x%%02x,0x%%02x" % (args.bytes * NUM_CHARS_HEX_BYTE)
else:
    DIFF_FMT_STR = "0x%%0%ix%s 0x%%02x%s 0x%%02x" % (args.bytes * NUM_CHARS_HEX_BYTE,
                                                     ADDR_PADDING, F1_PADDING)

offset = args.offset
differences = 0
with open(args.file1, 'rb') as f1:
    with open(args.file2, 'rb') as f2:
        size1 = os.path.getsize(args.file1)
        size2 = os.path.getsize(args.file2)
        if size1 != size2:
            print("Warning: file sizes differ", file=sys.stderr)
            print("%s size: %s" % (args.file1, byte_to_string(size1)),
                  file=sys.stderr)
            print("%s size: %s" % (args.file2, byte_to_string(size2)),
                  file=sys.stderr)
            print("Only comparing first %i bytes" % min(size1, size2),
                  file=sys.stderr)
            print("", file=sys.stderr)
        if not args.quiet:
            if args.csv:
                print("%s,%s,%s" % (HEADER_COL1, args.file1, args.file2))
            else:
                print("%s%s %s %s" % (HEADER_COL1, HEADER_PADDING,
                                      args.file1, args.file2))
        bytes1 = f1.read(args.chunksize)
        bytes2 = f2.read(args.chunksize)
        while bytes1 != b'' and bytes2 != b'':
            num_bytes = min(len(bytes1), len(bytes2))
            for i in range(num_bytes):
                if offset + i > MAX_OFFSET:
                    print("Offset exceeded given address size of %i bytes, quitting..."
                          % args.bytes, file=sys.stderr)
                    print_stats(offset + i - args.offset, differences)
                    sys.exit(1)
                byte1 = bytes1[i]
                byte2 = bytes2[i]
                if byte1 != byte2:
                    if not args.quiet:
                        print(DIFF_FMT_STR % (offset+i, byte1, byte2))
                    differences += 1
            offset += num_bytes
            bytes1 = f1.read(args.chunksize)
            bytes2 = f2.read(args.chunksize)

print_stats(offset - args.offset, differences)
