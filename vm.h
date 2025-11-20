#ifndef VM_H
#define VM_H

#include <stdint.h>

#define STACK_SIZE 1024
#define GLOBAL_SIZE 256
#define MAX_PROGRAM_SIZE 4096
#define MEMORY_SIZE 1024
#define MAX_VECTORS 128

// Instruction Set Architecture
typedef enum {
    OP_PUSH,          // Push value onto stack
    OP_ADD,           // Add top two stack values
    OP_SUB,           // Subtract top two stack values
    OP_MUL,           // Multiply top two stack values
    OP_DIV,           // Divide top two stack values
    OP_PRINT,         // Print top stack value
    OP_STORE,         // Store top stack value to global variable
    OP_LOAD,          // Load global variable onto stack
    OP_VECTOR,        // Create vector from N stack values, push pointer
    OP_DOT,           // Calculate dot product of two vectors, push result
    OP_RELU,          // ReLU activation: max(0, x)
    OP_GT,            // Greater than: push 1.0 if a > b, else 0.0
    OP_LT,            // Less than: push 1.0 if a < b, else 0.0
    OP_EQ,            // Equal: push 1.0 if a == b, else 0.0
    OP_JUMP_IF_FALSE, // Jump if top of stack is false (0.0)
    OP_JUMP,          // Unconditional jump
    OP_RAND,          // Generate random number [0.0, 1.0) and push
    OP_INPUT,         // Read floating-point number from stdin and push
    OP_SAVE_FILE,     // Save memory array state to disk
    OP_LOAD_FILE,     // Load memory array state from disk
    OP_HALT           // Halt execution
} OpCode;

// Vector metadata structure
typedef struct {
    int size;      // Number of elements
    int address;   // Address in memory array
} VectorInfo;

// Virtual Machine structure
typedef struct {
    double stack[STACK_SIZE];      // Stack for decimal precision
    int sp;                         // Stack pointer
    int ip;                         // Instruction pointer
    double globals[GLOBAL_SIZE];   // Global variables
    double memory[MEMORY_SIZE];    // Heap memory for vectors
    VectorInfo vectors[MAX_VECTORS]; // Vector metadata table
    int next_vector_index;         // Next available vector slot
    int next_memory_address;       // Next available memory address
    uint8_t code[MAX_PROGRAM_SIZE]; // Program bytecode
    int code_size;                  // Size of loaded program
} VM;

// Function prototypes
VM* vm_create(void);
void vm_destroy(VM* vm);
int vm_load_program(VM* vm, const char* filename);
void vm_execute(VM* vm);

#endif // VM_H

