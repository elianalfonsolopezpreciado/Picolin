# Picolin Programming Language MVP

A fully functional MVP for the Picolin programming language consisting of a Python compiler and a high-performance C virtual machine.

## Architecture

### Components

1. **Virtual Machine (C99)**: Stack-based VM with double precision arithmetic
2. **Compiler (Python)**: Lexer, parser, and bytecode generator

### Instruction Set

- `OP_PUSH`: Push value onto stack
- `OP_ADD`: Add top two stack values
- `OP_SUB`: Subtract top two stack values
- `OP_MUL`: Multiply top two stack values
- `OP_DIV`: Divide top two stack values
- `OP_PRINT`: Print top stack value
- `OP_STORE`: Store top stack value to global variable
- `OP_LOAD`: Load global variable onto stack
- `OP_HALT`: Halt execution

## Syntax

- **Assignment**: `variable <- expression`
- **Print**: `print expression`
- **Operators**: `+`, `-`, `*`, `/` (with proper precedence)
- **Numbers**: Integers and floating-point numbers
- **Variables**: Alphanumeric identifiers starting with letter or underscore
- **Comments**: Lines starting with `#` are ignored

## Building and Running

### Quick Start (One-line Instructions)

**Linux/macOS:**
```bash
gcc -std=c99 -Wall -Wextra -O2 -o vm vm.c && python3 compiler.py example.picolin program.bin && ./vm program.bin
```

**Windows (PowerShell):**
```powershell
gcc -std=c99 -Wall -Wextra -O2 -o vm.exe vm.c; python compiler.py example.picolin program.bin; .\vm.exe program.bin
```

**Windows (CMD):**
```cmd
gcc -std=c99 -Wall -Wextra -O2 -o vm.exe vm.c && python compiler.py example.picolin program.bin && vm.exe program.bin
```

### Using Build Scripts

**Linux/macOS:**
```bash
# Make build script executable
chmod +x build.sh

# Build and run
./build.sh
```

**Windows:**
```cmd
# Run build script
build.bat
```

### Manual Steps

**Step 1: Compile the VM**
```bash
# Linux/macOS
gcc -std=c99 -Wall -Wextra -O2 -o vm vm.c

# Windows
gcc -std=c99 -Wall -Wextra -O2 -o vm.exe vm.c
```

**Step 2: Compile Picolin source to bytecode**
```bash
# Linux/macOS
python3 compiler.py example.picolin program.bin

# Windows
python compiler.py example.picolin program.bin
```

**Step 3: Run the VM**
```bash
# Linux/macOS
./vm program.bin

# Windows
vm.exe program.bin
```

## Example

The included `example.picolin` file contains:
```
# Complex mathematical operation example
# Calculate: (3.14 * 2.5 + 1.5) / 2.0 - 0.25

result <- 3.14 * 2.5 + 1.5 / 2.0 - 0.25
print result
```

Expected output:
```
8.35
```
(Note: Due to floating-point precision, you may see `8.350000000000001` or similar)

## File Structure

- `vm.h` - VM header with struct and opcode definitions
- `vm.c` - VM implementation with fetch-decode-execute loop
- `compiler.py` - Python compiler with lexer and parser
- `example.picolin` - Sample Picolin program
- `build.sh` - Build script for Unix systems
- `build.bat` - Build script for Windows
- `README.md` - This file

## Requirements

- GCC compiler (C99 support)
- Python 3.x
- Standard C library
- Python struct module (built-in)

## Technical Details

### VM Architecture

The VM uses a stack-based architecture optimized for decimal precision:
- **Stack**: Array of doubles (1024 elements)
- **Globals**: Array of doubles (256 variables)
- **Instruction Format**: 
  - Opcode: 1 byte
  - Operands: 4 bytes (int) or 8 bytes (double) as needed

### Compiler Architecture

The compiler uses a recursive descent parser with operator precedence:
- **Lexer**: Regex-based tokenization
- **Parser**: Recursive descent with proper operator precedence
- **Code Generation**: Direct bytecode emission using Python's struct module

### Bytecode Format

- Opcodes are single bytes (0-8)
- Double values are stored in little-endian format (8 bytes)
- Integer indices are stored in little-endian format (4 bytes)
