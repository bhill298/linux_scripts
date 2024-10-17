#!/bin/bash
# sudo apt install nasm binutils
# take an asm file and dump its output bytes
if [ $# -eq 0]; then
    echo "Usage: $(basename $0) <input asm file> <?raw>"
    exit 1
fi
INPUT_FILE=$1
RAW_MODE=$2
TIMP_FILE=$(mktemp)
pre="0x"
suf=","
if [ -z "$TMP_FILE" ]; then
    echo "Error creating tmp directory"
    exit 1
fi
trap 'rm -rf $TMP_FILE' EXIT
nasm -O0 -f elf64 $INPUT_FILE -o $TMP_FILE
if [ $? -ne 0 ]; then
    exit $?
fi
if [ ! -z "$RAW_MODE" ]; then
    text=$(objcopy -O binary -j .text $TMP_FILE >(cat) | hexdump -ve "1/1 \"${pre}%.2x${suf}\"") && echo "bytes([${text%$suf}])"
else
    objdump -r -M intel --visualize-jumps=color -d $TMP_FILE | tail -n +7
fi
