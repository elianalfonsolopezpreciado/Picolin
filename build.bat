@echo off
REM Build script for Picolin VM and compiler (Windows)

echo Building Picolin Virtual Machine...
gcc -std=c99 -Wall -Wextra -O2 -o vm.exe vm.c

if %errorlevel% neq 0 (
    echo VM compilation failed!
    exit /b 1
)

echo VM compiled successfully!
echo.
echo Compiling example.picolin...
python compiler.py example.picolin program.bin

if %errorlevel% neq 0 (
    echo Compilation failed!
    exit /b 1
)

echo.
echo Running program...
vm.exe program.bin

