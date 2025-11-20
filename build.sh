#!/bin/bash
# Build script for Picolin VM and compiler

echo "Building Picolin Virtual Machine..."
gcc -std=c99 -Wall -Wextra -O2 -o vm vm.c

if [ $? -eq 0 ]; then
    echo "VM compiled successfully!"
else
    echo "VM compilation failed!"
    exit 1
fi

echo ""
echo "Compiling example.picolin..."
python3 compiler.py example.picolin program.bin

if [ $? -eq 0 ]; then
    echo ""
    echo "Running program..."
    ./vm program.bin
else
    echo "Compilation failed!"
    exit 1
fi

