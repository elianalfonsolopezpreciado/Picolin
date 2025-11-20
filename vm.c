#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>
#include "vm.h"

// Create and initialize a new VM instance
VM* vm_create(void) {
    VM* vm = (VM*)malloc(sizeof(VM));
    if (!vm) {
        fprintf(stderr, "Error: Failed to allocate VM memory\n");
        return NULL;
    }
    
    // Initialize VM state
    memset(vm->stack, 0, sizeof(vm->stack));
    memset(vm->globals, 0, sizeof(vm->globals));
    memset(vm->memory, 0, sizeof(vm->memory));
    memset(vm->vectors, 0, sizeof(vm->vectors));
    memset(vm->code, 0, sizeof(vm->code));
    vm->sp = -1;
    vm->ip = 0;
    vm->code_size = 0;
    vm->next_vector_index = 0;
    vm->next_memory_address = 0;
    
    return vm;
}

// Destroy VM instance
void vm_destroy(VM* vm) {
    if (vm) {
        free(vm);
    }
}

// Load binary program from file
int vm_load_program(VM* vm, const char* filename) {
    FILE* file = fopen(filename, "rb");
    if (!file) {
        fprintf(stderr, "Error: Cannot open file %s\n", filename);
        return 0;
    }
    
    // Read file size
    fseek(file, 0, SEEK_END);
    long file_size = ftell(file);
    fseek(file, 0, SEEK_SET);
    
    if (file_size > MAX_PROGRAM_SIZE) {
        fprintf(stderr, "Error: Program too large (max %d bytes)\n", MAX_PROGRAM_SIZE);
        fclose(file);
        return 0;
    }
    
    // Read program into VM code array
    vm->code_size = (int)fread(vm->code, 1, file_size, file);
    fclose(file);
    
    if (vm->code_size == 0) {
        fprintf(stderr, "Error: Failed to read program\n");
        return 0;
    }
    
    return 1;
}

// Push value onto stack
static void push(VM* vm, double value) {
    if (vm->sp >= STACK_SIZE - 1) {
        fprintf(stderr, "Error: Stack overflow\n");
        return;
    }
    vm->stack[++vm->sp] = value;
}

// Pop value from stack
static double pop(VM* vm) {
    if (vm->sp < 0) {
        fprintf(stderr, "Error: Stack underflow\n");
        return 0.0;
    }
    return vm->stack[vm->sp--];
}

// Fetch next byte from program
static uint8_t fetch_byte(VM* vm) {
    if (vm->ip >= vm->code_size) {
        fprintf(stderr, "Error: Instruction pointer out of bounds\n");
        return OP_HALT;
    }
    return vm->code[vm->ip++];
}

// Fetch next double value from program (8 bytes)
static double fetch_double(VM* vm) {
    if (vm->ip + sizeof(double) > vm->code_size) {
        fprintf(stderr, "Error: Cannot fetch double value\n");
        return 0.0;
    }
    
    double value;
    memcpy(&value, &vm->code[vm->ip], sizeof(double));
    vm->ip += sizeof(double);
    return value;
}

// Fetch next integer value from program (4 bytes)
static int fetch_int(VM* vm) {
    if (vm->ip + sizeof(int) > vm->code_size) {
        fprintf(stderr, "Error: Cannot fetch int value\n");
        return 0;
    }
    
    int value;
    memcpy(&value, &vm->code[vm->ip], sizeof(int));
    vm->ip += sizeof(int);
    return value;
}

// Main execution loop: fetch-decode-execute
void vm_execute(VM* vm) {
    vm->ip = 0;
    
    while (vm->ip < vm->code_size) {
        uint8_t opcode = fetch_byte(vm);
        
        switch (opcode) {
            case OP_PUSH: {
                double value = fetch_double(vm);
                push(vm, value);
                break;
            }
            
            case OP_ADD: {
                double b = pop(vm);
                double a = pop(vm);
                push(vm, a + b);
                break;
            }
            
            case OP_SUB: {
                double b = pop(vm);
                double a = pop(vm);
                push(vm, a - b);
                break;
            }
            
            case OP_MUL: {
                double b = pop(vm);
                double a = pop(vm);
                push(vm, a * b);
                break;
            }
            
            case OP_DIV: {
                double b = pop(vm);
                double a = pop(vm);
                if (b == 0.0) {
                    fprintf(stderr, "Error: Division by zero\n");
                    return;
                }
                push(vm, a / b);
                break;
            }
            
            case OP_PRINT: {
                if (vm->sp >= 0) {
                    printf("%.15g\n", vm->stack[vm->sp]);
                    vm->sp--; // Pop after printing
                } else {
                    fprintf(stderr, "Error: Nothing to print\n");
                }
                break;
            }
            
            case OP_STORE: {
                int var_index = fetch_int(vm);
                if (var_index < 0 || var_index >= GLOBAL_SIZE) {
                    fprintf(stderr, "Error: Invalid variable index\n");
                    return;
                }
                double value = pop(vm);
                vm->globals[var_index] = value;
                break;
            }
            
            case OP_LOAD: {
                int var_index = fetch_int(vm);
                if (var_index < 0 || var_index >= GLOBAL_SIZE) {
                    fprintf(stderr, "Error: Invalid variable index\n");
                    return;
                }
                push(vm, vm->globals[var_index]);
                break;
            }
            
            case OP_VECTOR: {
                // Read vector size from instruction
                int vector_size = fetch_int(vm);
                
                if (vector_size <= 0 || vector_size > MEMORY_SIZE) {
                    fprintf(stderr, "Error: Invalid vector size %d\n", vector_size);
                    return;
                }
                
                // Check if we have enough memory
                if (vm->next_memory_address + vector_size > MEMORY_SIZE) {
                    fprintf(stderr, "Error: Out of memory\n");
                    return;
                }
                
                // Check if we have space in vector table
                if (vm->next_vector_index >= MAX_VECTORS) {
                    fprintf(stderr, "Error: Too many vectors\n");
                    return;
                }
                
                // Pop vector_size values from stack and store in memory
                int address = vm->next_memory_address;
                for (int i = vector_size - 1; i >= 0; i--) {
                    if (vm->sp < 0) {
                        fprintf(stderr, "Error: Not enough values on stack for vector\n");
                        return;
                    }
                    vm->memory[address + i] = pop(vm);
                }
                
                // Store vector metadata
                vm->vectors[vm->next_vector_index].size = vector_size;
                vm->vectors[vm->next_vector_index].address = address;
                
                // Push vector pointer (index in vectors table) onto stack
                push(vm, (double)vm->next_vector_index);
                
                // Update memory and vector indices
                vm->next_memory_address += vector_size;
                vm->next_vector_index++;
                break;
            }
            
            case OP_DOT: {
                // Pop two vector pointers from stack
                double ptr2_val = pop(vm);
                double ptr1_val = pop(vm);
                
                int ptr1 = (int)ptr1_val;
                int ptr2 = (int)ptr2_val;
                
                // Validate vector pointers
                if (ptr1 < 0 || ptr1 >= vm->next_vector_index ||
                    ptr2 < 0 || ptr2 >= vm->next_vector_index) {
                    fprintf(stderr, "Error: Invalid vector pointer\n");
                    return;
                }
                
                VectorInfo* vec1 = &vm->vectors[ptr1];
                VectorInfo* vec2 = &vm->vectors[ptr2];
                
                // Check if vectors have same size
                if (vec1->size != vec2->size) {
                    fprintf(stderr, "Error: Vectors must have same size for dot product (got %d and %d)\n", 
                            vec1->size, vec2->size);
                    return;
                }
                
                // Calculate dot product
                double dot_product = 0.0;
                for (int i = 0; i < vec1->size; i++) {
                    dot_product += vm->memory[vec1->address + i] * vm->memory[vec2->address + i];
                }
                
                // Push result onto stack
                push(vm, dot_product);
                break;
            }
            
            case OP_RELU: {
                double value = pop(vm);
                if (value < 0.0) {
                    push(vm, 0.0);
                } else {
                    push(vm, value);
                }
                break;
            }
            
            case OP_GT: {
                double b = pop(vm);
                double a = pop(vm);
                push(vm, (a > b) ? 1.0 : 0.0);
                break;
            }
            
            case OP_LT: {
                double b = pop(vm);
                double a = pop(vm);
                push(vm, (a < b) ? 1.0 : 0.0);
                break;
            }
            
            case OP_EQ: {
                double b = pop(vm);
                double a = pop(vm);
                // Use epsilon for floating point comparison
                double epsilon = 1e-9;
                push(vm, ((a - b) < epsilon && (b - a) < epsilon) ? 1.0 : 0.0);
                break;
            }
            
            case OP_JUMP_IF_FALSE: {
                int offset = fetch_int(vm);
                double condition = pop(vm);
                if (condition == 0.0) {
                    // Jump: add offset to instruction pointer
                    vm->ip += offset;
                }
                break;
            }
            
            case OP_JUMP: {
                int offset = fetch_int(vm);
                // Unconditional jump: add offset to instruction pointer
                vm->ip += offset;
                break;
            }
            
            case OP_RAND: {
                // Generate random number between 0.0 and 1.0
                double random_value = (double)rand() / (double)RAND_MAX;
                push(vm, random_value);
                break;
            }
            
            case OP_INPUT: {
                // Prompt user and read floating-point number
                printf("? ");
                fflush(stdout);  // Ensure prompt is displayed immediately
                double value;
                if (scanf("%lf", &value) != 1) {
                    fprintf(stderr, "Error: Failed to read input\n");
                    value = 0.0;
                }
                push(vm, value);
                break;
            }
            
            case OP_SAVE_FILE: {
                // Save entire memory state to disk
                const char* filename = "memory.dump";
                FILE* file = fopen(filename, "wb");
                if (!file) {
                    fprintf(stderr, "Error: Cannot create file %s\n", filename);
                    break;
                }
                
                // Write memory state: next_memory_address, next_vector_index, memory array, vectors array
                fwrite(&vm->next_memory_address, sizeof(int), 1, file);
                fwrite(&vm->next_vector_index, sizeof(int), 1, file);
                fwrite(vm->memory, sizeof(double), MEMORY_SIZE, file);
                fwrite(vm->vectors, sizeof(VectorInfo), MAX_VECTORS, file);
                
                fclose(file);
                break;
            }
            
            case OP_LOAD_FILE: {
                // Load entire memory state from disk
                const char* filename = "memory.dump";
                FILE* file = fopen(filename, "rb");
                if (!file) {
                    fprintf(stderr, "Error: Cannot open file %s\n", filename);
                    break;
                }
                
                // Read memory state: next_memory_address, next_vector_index, memory array, vectors array
                if (fread(&vm->next_memory_address, sizeof(int), 1, file) != 1 ||
                    fread(&vm->next_vector_index, sizeof(int), 1, file) != 1 ||
                    fread(vm->memory, sizeof(double), MEMORY_SIZE, file) != MEMORY_SIZE ||
                    fread(vm->vectors, sizeof(VectorInfo), MAX_VECTORS, file) != MAX_VECTORS) {
                    fprintf(stderr, "Error: Failed to read from file %s\n", filename);
                    fclose(file);
                    break;
                }
                
                fclose(file);
                break;
            }
            
            case OP_HALT: {
                return;
            }
            
            default: {
                fprintf(stderr, "Error: Unknown opcode %d at position %d\n", opcode, vm->ip - 1);
                return;
            }
        }
    }
}

// Main entry point
int main(int argc, char* argv[]) {
    // Initialize random seed
    srand(time(NULL));
    
    const char* filename = "program.bin";
    
    if (argc > 1) {
        filename = argv[1];
    }
    
    VM* vm = vm_create();
    if (!vm) {
        return 1;
    }
    
    if (!vm_load_program(vm, filename)) {
        vm_destroy(vm);
        return 1;
    }
    
    vm_execute(vm);
    
    vm_destroy(vm);
    return 0;
}

