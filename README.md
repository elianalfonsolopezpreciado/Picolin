# Picolin Programming Language

Picolin is a dynamic, high-level programming language designed for rapid prototyping and educational purposes. It features a simple, clean syntax, a Python-based compiler, and a high-performance, stack-based virtual machine written in C99. The language is particularly well-suited for tasks involving numerical computation, basic machine learning, and interactive scripts.

## Features

- **Simple & Intuitive Syntax**: Easy-to-learn syntax for assignments, printing, and arithmetic.
- **Vector Operations**: First-class support for vectors, including dot products, making it ideal for linear algebra and scientific computing.
- **Control Flow**: `if/else` and `while` loops for building complex logic.
- **File I/O**: `save` and `load` commands to persist and restore the VM's memory state.
- **Interactive I/O**: `input` command to read user input and `print` to display output.
- **Multi-language Support**: Keywords available in both English and Spanish (e.g., `print` and `imprimir`).
- **Extensible**: The VM and compiler are designed to be easily extended with new features.

## Getting Started

### Quick Start

**Linux/macOS:**
```bash
./build.sh
```

**Windows:**
```cmd
build.bat
```

This will compile the C virtual machine, compile the example Picolin code (`example.picolin`) into bytecode (`program.bin`), and execute it.

## Syntax Overview

The syntax is designed to be straightforward and readable.

| Syntax Element        | Example                                     | Description                                         |
| --------------------- | ------------------------------------------- | --------------------------------------------------- |
| **Comments**          | `# This is a comment`                       | Lines starting with `#` are ignored.                |
| **Assignment**        | `my_var <- 42`                              | Assign a value to a variable.                       |
| **Printing**          | `print my_var`                              | Print the value of a variable or expression.        |
| **Arithmetic**        | `result <- (a + b) * c`                     | Standard arithmetic operators with precedence.      |
| **Vectors**           | `my_vector <- [1.0, 2.0, 3.0]`              | Create a vector of floating-point numbers.          |
| **Dot Product**       | `dp <- vec1 dot vec2`                       | Calculate the dot product of two vectors.           |
| **If/Else Statement** | `if x > 10 ... else ... end`                | Conditional execution. `else` is optional.          |
| **While Loop**        | `while i < 10 ... end`                      | Loop while a condition is true.                     |
| **User Input**        | `user_val <- input`                         | Read a number from standard input.                  |
| **Random Number**     | `r <- rand`                                 | Get a random floating-point number between 0 and 1. |
| **File I/O**          | `save` / `load`                             | Save or load the VM's global memory to a file.      |

## Example: A Simple Neural Network Neuron

Picolin's support for vector operations makes it easy to implement concepts from machine learning. Here is an example of a single artificial neuron that computes the dot product of an input vector and a weight vector.

```picolin
# Artificial Neuron Example
# Simulates a single neuron with weights and inputs
# Calculates: output = weights · inputs (dot product)

# Define weight vector [0.5, -0.3, 0.8]
weights <- [0.5, -0.3, 0.8]

# Define input vector [1.0, 2.0, 0.5]
inputs <- [1.0, 2.0, 0.5]

# Calculate dot product (neuron output)
output <- weights dot inputs

# Print the result
print output
```

**To run this example:**

1.  Save the code above as `neural.picolin`.
2.  Compile it: `python3 compiler.py neural.picolin neural.bin`
3.  Run it: `./vm neural.bin`

**Expected output:**
```
0.3
```

## Instruction Set (Opcodes)

The Picolin VM uses the following set of instructions.

| Opcode             | ID | Description                                            |
| ------------------ | -- | ------------------------------------------------------ |
| `OP_PUSH`          | 0  | Push a double value onto the stack.                    |
| `OP_ADD`           | 1  | Add the top two stack values.                          |
| `OP_SUB`           | 2  | Subtract the top two stack values.                     |
| `OP_MUL`           | 3  | Multiply the top two stack values.                     |
| `OP_DIV`           | 4  | Divide the top two stack values.                       |
| `OP_PRINT`         | 5  | Print the top value of the stack.                      |
| `OP_STORE`         | 6  | Store the top stack value to a global variable.        |
| `OP_LOAD`          | 7  | Load a global variable onto the stack.                 |
| `OP_VECTOR`        | 8  | Create a vector from values on the stack.              |
| `OP_DOT`           | 9  | Calculate the dot product of the top two vectors.      |
| `OP_RELU`          | 10 | Apply the ReLU activation function to the top value.   |
| `OP_GT`            | 11 | Greater than comparison.                               |
| `OP_LT`            | 12 | Less than comparison.                                  |
| `OP_EQ`            | 13 | Equality comparison.                                   |
| `OP_JUMP_IF_FALSE` | 14 | Jump to a new instruction pointer if top of stack is 0. |
| `OP_JUMP`          | 15 | Unconditionally jump to a new instruction pointer.     |
| `OP_RAND`          | 16 | Push a random float (0-1) onto the stack.              |
| `OP_INPUT`         | 17 | Read a double from stdin and push it onto the stack.   |
| `OP_SAVE_FILE`     | 18 | Save global variables to `picolin.mem`.                |
| `OP_LOAD_FILE`     | 19 | Load global variables from `picolin.mem`.              |
| `OP_HALT`          | 20 | Halt execution.                                        |

## Architecture

-   **Virtual Machine**: A stack-based VM written in C99 for performance.
-   **Compiler**: A recursive descent parser and bytecode generator written in Python.

## Requirements

-   GCC compiler (or any C99-compatible compiler)
-   Python 3.x
