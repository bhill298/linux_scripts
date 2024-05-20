#!/usr/bin/env python3.7
import argparse
import inspect
import pprint
import sys

# for 64 bits x86


def pad_start(s, to_len=64, pad='0'):
    return s.rjust(to_len, pad)


def to_bin_str(val):
    return bin(val)[2:]


def build_vaddr(offset, l4, l3, l2=None, l1=None):
    if l2 is None and l1 is None:
        val = pad_start(to_bin_str(l4), to_len=9, pad='0') + \
              pad_start(to_bin_str(l3), to_len=9, pad='0') + \
              pad_start(to_bin_str(offset), to_len=30, pad='0')
    elif l1 is None:
        val = pad_start(to_bin_str(l4), to_len=9, pad='0') + \
              pad_start(to_bin_str(l3), to_len=9, pad='0') + \
              pad_start(to_bin_str(l2), to_len=9, pad='0') + \
              pad_start(to_bin_str(offset), to_len=21, pad='0')
    else:
        val = pad_start(to_bin_str(l4), to_len=9, pad='0') + \
              pad_start(to_bin_str(l3), to_len=9, pad='0') + \
              pad_start(to_bin_str(l2), to_len=9, pad='0') + \
              pad_start(to_bin_str(l1), to_len=9, pad='0') + \
              pad_start(to_bin_str(offset), to_len=12, pad='0')
    return int(pad_start(val, pad=val[0]), 2)


def translate_vaddr(vaddr):
    vaddr = pad_start(to_bin_str(vaddr), 64)
    print('unused 16 bits:', vaddr[0:16])
    print('L4 bits:', vaddr[16:25], '  ', hex(int(vaddr[16:25], 2)))
    print('L3 bits:', vaddr[25:34], '  ', hex(int(vaddr[25:34], 2)))
    print('L2 bits:', vaddr[34:43], '  ', hex(int(vaddr[34:43], 2)))
    print('L1 bits:', vaddr[43:52], '  ', hex(int(vaddr[43:52], 2)))
    print('offset :', vaddr[52:64], hex(int(vaddr[52:64], 2)))


def extract_pfn(pte):
    pfn = int(to_bin_str(pte)[24:52], 2)
    print('pfn is', hex(pfn), 'to addr', hex(pfn) + '000')


def print_help():
    print('Available functions:')
    pprint.pprint([el[0] for el in inspect.getmembers(sys.modules[__name__], inspect.isfunction)
                   if el[0] != 'main' and not el[0].startswith('_')])
    

def main():
    parser = argparse.ArgumentParser(description='Stuff')
    args = parser.parse_args()
    print_help()
    import IPython; IPython.embed()


if __name__ == "__main__":
    main()
