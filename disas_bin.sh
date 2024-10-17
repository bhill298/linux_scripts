#!/bin/bash
objdump -m i386:x86-64 -b binary -r -M intel --visualize-jumps=color -D $1 | tail -n +8
