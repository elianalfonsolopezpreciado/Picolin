#!/usr/bin/env python3
"""
Picolin Compiler
A compiler for the Picolin programming language that generates bytecode
for the stack-based virtual machine.
"""

import re
import struct
from typing import List, Tuple, Optional

# OpCode definitions (must match vm.h)
OP_PUSH = 0
OP_ADD = 1
OP_SUB = 2
OP_MUL = 3
OP_DIV = 4
OP_PRINT = 5
OP_STORE = 6
OP_LOAD = 7
OP_VECTOR = 8
OP_DOT = 9
OP_RELU = 10
OP_GT = 11
OP_LT = 12
OP_EQ = 13
OP_JUMP_IF_FALSE = 14
OP_JUMP = 15
OP_RAND = 16
OP_INPUT = 17
OP_SAVE_FILE = 18
OP_LOAD_FILE = 19
OP_HALT = 20

# Token types
TOKEN_NUMBER = 'NUMBER'
TOKEN_IDENTIFIER = 'IDENTIFIER'
TOKEN_ARROW = 'ARROW'  # <-
TOKEN_PRINT = 'PRINT'
TOKEN_PLUS = 'PLUS'
TOKEN_MINUS = 'MINUS'
TOKEN_MULTIPLY = 'MULTIPLY'
TOKEN_DIVIDE = 'DIVIDE'
TOKEN_LPAREN = 'LPAREN'
TOKEN_RPAREN = 'RPAREN'
TOKEN_LBRACKET = 'LBRACKET'  # [
TOKEN_RBRACKET = 'RBRACKET'  # ]
TOKEN_COMMA = 'COMMA'  # ,
TOKEN_DOT = 'DOT'  # dot keyword
TOKEN_RELU = 'RELU'  # relu keyword
TOKEN_IF = 'IF'  # if keyword
TOKEN_WHILE = 'WHILE'  # while keyword
TOKEN_ELSE = 'ELSE'  # else keyword
TOKEN_END = 'END'  # end keyword
TOKEN_RAND = 'RAND'  # rand keyword
TOKEN_INPUT = 'INPUT'  # input keyword
TOKEN_SAVE = 'SAVE'  # save keyword
TOKEN_LOAD = 'LOAD'  # load keyword
TOKEN_GT = 'GT'  # >
TOKEN_LT = 'LT'  # <
TOKEN_EQ = 'EQ'  # ==
TOKEN_EOF = 'EOF'

# Token regex patterns
# IMPORTANT: Keywords must come BEFORE TOKEN_IDENTIFIER to avoid ambiguity
# IMPORTANT: NUMBER must come BEFORE TOKEN_MINUS to match negative numbers
# IMPORTANT: == must come before = (if we add = later)
# IMPORTANT: Keywords use word boundaries to avoid matching inside identifiers
TOKEN_PATTERNS = [
    (TOKEN_NUMBER, r'-?\d+\.?\d*'),  # Numbers (integers and floats, optionally negative)
    (TOKEN_ARROW, r'<-'),  # Assignment arrow
    (TOKEN_PRINT, r'\bprint\b'),  # Print keyword (English) - word boundary
    (TOKEN_PRINT, r'\bimprimir\b'),  # Print keyword (Spanish) - word boundary
    (TOKEN_DOT, r'\bdot\b'),  # Dot product keyword - word boundary
    (TOKEN_RELU, r'\brelu\b'),  # ReLU activation keyword - word boundary
    (TOKEN_IF, r'\bif\b'),  # if keyword - word boundary
    (TOKEN_WHILE, r'\bwhile\b'),  # while keyword - word boundary
    (TOKEN_ELSE, r'\belse\b'),  # else keyword - word boundary
    (TOKEN_END, r'\bend\b'),  # end keyword - word boundary
    (TOKEN_RAND, r'\brand\b'),  # rand keyword - word boundary
    (TOKEN_INPUT, r'\binput\b'),  # input keyword - word boundary
    (TOKEN_SAVE, r'\bsave\b'),  # save keyword - word boundary
    (TOKEN_LOAD, r'\bload\b'),  # load keyword - word boundary
    (TOKEN_IDENTIFIER, r'[a-zA-Z_][a-zA-Z0-9_]*'),  # Identifiers (must be after keywords)
    (TOKEN_PLUS, r'\+'),
    (TOKEN_MINUS, r'-'),  # Subtraction operator (only matches when not part of number)
    (TOKEN_MULTIPLY, r'\*'),
    (TOKEN_DIVIDE, r'/'),
    (TOKEN_EQ, r'=='),  # Equality operator (must come before other operators)
    (TOKEN_GT, r'>'),  # Greater than
    (TOKEN_LT, r'<'),  # Less than
    (TOKEN_LPAREN, r'\('),
    (TOKEN_RPAREN, r'\)'),
    (TOKEN_LBRACKET, r'\['),  # Left bracket
    (TOKEN_RBRACKET, r'\]'),  # Right bracket
    (TOKEN_COMMA, r','),  # Comma
    (r'\s+', None),  # Skip whitespace
]


class Token:
    def __init__(self, type: str, value: str, position: int):
        self.type = type
        self.value = value
        self.position = position
    
    def __repr__(self):
        return f"Token({self.type}, {self.value!r})"


class Lexer:
    def __init__(self, source: str):
        # Remove comments (lines starting with # or # anywhere)
        lines = source.split('\n')
        cleaned_lines = []
        for line in lines:
            comment_pos = line.find('#')
            if comment_pos >= 0:
                line = line[:comment_pos]
            cleaned_lines.append(line)
        self.source = '\n'.join(cleaned_lines)
        self.position = 0
        self.tokens = []
    
    def tokenize(self) -> List[Token]:
        """Tokenize the source code using regex patterns."""
        while self.position < len(self.source):
            matched = False
            
            for item in TOKEN_PATTERNS:
                # Handle both (token_type, pattern) and (pattern, None) formats
                if len(item) == 2:
                    if item[1] is None:
                        # Format: (pattern, None) for whitespace
                        pattern_str = item[0]
                        token_type = None
                    else:
                        # Format: (token_type, pattern) for tokens
                        token_type = item[0]
                        pattern_str = item[1]
                else:
                    continue
                
                regex = re.compile(pattern_str)
                match = regex.match(self.source, self.position)
                
                if match:
                    matched = True
                    value = match.group(0)
                    
                    if token_type:  # Skip whitespace (None type)
                        # Keywords are already matched by their specific patterns above
                        # This ensures 'print' and 'imprimir' are TOKEN_PRINT, not TOKEN_IDENTIFIER
                        self.tokens.append(Token(token_type, value, self.position))
                    
                    self.position = match.end()
                    break
            
            if not matched:
                # Show context around error
                start = max(0, self.position - 10)
                end = min(len(self.source), self.position + 10)
                context = self.source[start:end]
                raise SyntaxError(f"Unexpected character '{self.source[self.position]}' at position {self.position}. Context: {repr(context)}")
        
        self.tokens.append(Token(TOKEN_EOF, '', self.position))
        return self.tokens


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
        self.bytecode = []
        self.variables = {}  # Map variable names to indices
        self.next_var_index = 0
    
    def peek(self) -> Token:
        """Look at current token without consuming it."""
        if self.current >= len(self.tokens):
            return self.tokens[-1]  # Return EOF
        return self.tokens[self.current]
    
    def advance(self) -> Token:
        """Consume and return current token."""
        if self.current < len(self.tokens):
            self.current += 1
        return self.tokens[self.current - 1]
    
    def get_var_index(self, name: str) -> int:
        """Get or create variable index."""
        if name not in self.variables:
            self.variables[name] = self.next_var_index
            self.next_var_index += 1
        return self.variables[name]
    
    def emit_byte(self, byte: int):
        """Emit a single byte."""
        self.bytecode.append(byte)
    
    def emit_double(self, value: float):
        """Emit a double value (8 bytes)."""
        packed = struct.pack('<d', value)  # Little-endian double
        self.bytecode.extend(packed)
    
    def emit_int(self, value: int):
        """Emit an integer value (4 bytes)."""
        packed = struct.pack('<i', value)  # Little-endian int
        self.bytecode.extend(packed)
    
    def patch_int(self, position: int, value: int):
        """Patch an integer value at a specific position in bytecode."""
        packed = struct.pack('<i', value)
        for i, byte in enumerate(packed):
            self.bytecode[position + i] = byte
    
    def get_code_position(self) -> int:
        """Get current bytecode position."""
        return len(self.bytecode)
    
    def parse_expression(self):
        """Parse expression with operator precedence (shunting yard algorithm)."""
        # Parse using recursive descent with precedence
        # Comparisons have lower precedence than arithmetic
        return self.parse_comparison()
    
    def parse_additive(self):
        """Parse addition and subtraction (lower precedence)."""
        left = self.parse_multiplicative()
        
        while self.peek().type in (TOKEN_PLUS, TOKEN_MINUS):
            op = self.advance()
            right = self.parse_multiplicative()
            
            if op.type == TOKEN_PLUS:
                self.emit_byte(OP_ADD)
            else:
                self.emit_byte(OP_SUB)
        
        return left
    
    def parse_multiplicative(self):
        """Parse multiplication, division, and dot product (higher precedence)."""
        left = self.parse_unary()
        
        while self.peek().type in (TOKEN_MULTIPLY, TOKEN_DIVIDE, TOKEN_DOT):
            op = self.advance()
            right = self.parse_unary()
            
            if op.type == TOKEN_MULTIPLY:
                self.emit_byte(OP_MUL)
            elif op.type == TOKEN_DIVIDE:
                self.emit_byte(OP_DIV)
            elif op.type == TOKEN_DOT:
                self.emit_byte(OP_DOT)
        
        return left
    
    def parse_comparison(self):
        """Parse comparison operators (GT, LT, EQ) - lower precedence than arithmetic."""
        left = self.parse_additive()
        
        while self.peek().type in (TOKEN_GT, TOKEN_LT, TOKEN_EQ):
            op = self.advance()
            right = self.parse_additive()
            
            if op.type == TOKEN_GT:
                self.emit_byte(OP_GT)
            elif op.type == TOKEN_LT:
                self.emit_byte(OP_LT)
            elif op.type == TOKEN_EQ:
                self.emit_byte(OP_EQ)
        
        return left
    
    def parse_unary(self):
        """Parse unary operators and primary expressions."""
        if self.peek().type == TOKEN_RELU:
            self.advance()  # Consume 'relu'
            self.parse_primary()
            self.emit_byte(OP_RELU)
            return
        
        if self.peek().type == TOKEN_MINUS:
            self.advance()
            self.parse_primary()
            # Emit negation: 0 - value
            self.emit_byte(OP_PUSH)
            self.emit_double(0.0)
            self.emit_byte(OP_SUB)
            return
        
        return self.parse_primary()
    
    def parse_primary(self):
        """Parse primary expressions (numbers, identifiers, parentheses, vectors, rand, input)."""
        token = self.peek()
        
        if token.type == TOKEN_NUMBER:
            self.advance()
            value = float(token.value)
            self.emit_byte(OP_PUSH)
            self.emit_double(value)
            return value
        
        elif token.type == TOKEN_RAND:
            self.advance()  # Consume 'rand'
            self.emit_byte(OP_RAND)
            return None  # rand returns a value but we don't know it at compile time
        
        elif token.type == TOKEN_INPUT:
            self.advance()  # Consume 'input'
            self.emit_byte(OP_INPUT)
            return None  # input returns a value but we don't know it at compile time
        
        elif token.type == TOKEN_IDENTIFIER:
            self.advance()
            var_name = token.value
            var_index = self.get_var_index(var_name)
            self.emit_byte(OP_LOAD)
            self.emit_int(var_index)
            return var_name
        
        elif token.type == TOKEN_LPAREN:
            self.advance()  # Consume '('
            result = self.parse_expression()
            if self.peek().type != TOKEN_RPAREN:
                raise SyntaxError(f"Expected ')' at position {self.peek().position}")
            self.advance()  # Consume ')'
            return result
        
        elif token.type == TOKEN_LBRACKET:
            # Vector literal: [expr1, expr2, ...]
            self.advance()  # Consume '['
            elements = []
            
            # Check for empty vector
            if self.peek().type == TOKEN_RBRACKET:
                self.advance()  # Consume ']'
                # Empty vector - push size 0 and create vector
                self.emit_byte(OP_VECTOR)
                self.emit_int(0)
                return []
            
            # Parse first element
            self.parse_expression()
            elements.append(None)  # Placeholder
            
            # Parse remaining elements
            while self.peek().type == TOKEN_COMMA:
                self.advance()  # Consume ','
                self.parse_expression()
                elements.append(None)  # Placeholder
            
            if self.peek().type != TOKEN_RBRACKET:
                raise SyntaxError(f"Expected ']' at position {self.peek().position}")
            self.advance()  # Consume ']'
            
            # Emit OP_VECTOR with size
            vector_size = len(elements)
            self.emit_byte(OP_VECTOR)
            self.emit_int(vector_size)
            
            return elements
        
        else:
            raise SyntaxError(f"Unexpected token {token.type} at position {token.position}")
    
    def parse_statement(self):
        """Parse a statement."""
        token = self.peek()
        
        if token.type == TOKEN_WHILE:
            # while condition ... end
            self.advance()  # Consume 'while'
            
            # Save loop start position (where condition evaluation begins)
            loop_start_pos = self.get_code_position()
            
            # Parse condition
            self.parse_expression()
            
            # Emit OP_JUMP_IF_FALSE with placeholder offset (will jump to end if false)
            self.emit_byte(OP_JUMP_IF_FALSE)
            jump_if_false_pos = self.get_code_position()
            self.emit_int(0)  # Placeholder - will be patched
            
            # Parse loop body
            while self.peek().type != TOKEN_END:
                if self.peek().type == TOKEN_EOF:
                    raise SyntaxError(f"Expected 'end' at position {self.peek().position}")
                self.parse_statement()
            
            # At end of loop body, emit unconditional jump back to loop start
            self.emit_byte(OP_JUMP)
            jump_back_pos = self.get_code_position()
            self.emit_int(0)  # Placeholder - will be calculated
            
            # Calculate position after the jump instruction
            after_loop_pos = self.get_code_position()
            
            # Calculate negative offset to jump back to loop start
            # When OP_JUMP executes, ip is at after_loop_pos, so offset = loop_start_pos - after_loop_pos
            offset_back = loop_start_pos - after_loop_pos
            self.patch_int(jump_back_pos, offset_back)
            
            # Patch the OP_JUMP_IF_FALSE to jump to after the loop
            offset_to_end = after_loop_pos - jump_if_false_pos - 4  # -4 for the int we're patching
            self.patch_int(jump_if_false_pos, offset_to_end)
            
            # Consume 'end'
            if self.peek().type != TOKEN_END:
                raise SyntaxError(f"Expected 'end' at position {self.peek().position}")
            self.advance()
        
        elif token.type == TOKEN_IF:
            # if condition ... else ... end
            self.advance()  # Consume 'if'
            
            # Parse condition
            self.parse_expression()
            
            # Emit OP_JUMP_IF_FALSE with placeholder offset
            self.emit_byte(OP_JUMP_IF_FALSE)
            jump_if_false_pos = self.get_code_position()
            self.emit_int(0)  # Placeholder - will be patched
            
            # Parse then block
            while self.peek().type not in (TOKEN_ELSE, TOKEN_END, TOKEN_EOF):
                self.parse_statement()
            
            # Check if there's an else block
            has_else = self.peek().type == TOKEN_ELSE
            
            if has_else:
                # Emit jump to skip else block
                self.emit_byte(OP_JUMP)
                jump_else_pos = self.get_code_position()
                self.emit_int(0)  # Placeholder - will be patched
                
                # Patch the first jump (to else block)
                else_block_start = self.get_code_position()
                offset_to_else = else_block_start - jump_if_false_pos - 4  # -4 for the int we're patching
                self.patch_int(jump_if_false_pos, offset_to_else)
                
                # Consume 'else'
                self.advance()
                
                # Parse else block
                while self.peek().type != TOKEN_END:
                    if self.peek().type == TOKEN_EOF:
                        raise SyntaxError(f"Expected 'end' at position {self.peek().position}")
                    if self.peek().type == TOKEN_WHILE:
                        raise SyntaxError(f"Unexpected 'while' inside else block at position {self.peek().position}")
                    self.parse_statement()
                
                # Patch the second jump (skip else block)
                end_pos = self.get_code_position()
                offset_to_end = end_pos - jump_else_pos - 4
                self.patch_int(jump_else_pos, offset_to_end)
            else:
                # No else block - patch jump to end
                end_pos = self.get_code_position()
                offset_to_end = end_pos - jump_if_false_pos - 4
                self.patch_int(jump_if_false_pos, offset_to_end)
            
            # Consume 'end'
            if self.peek().type != TOKEN_END:
                raise SyntaxError(f"Expected 'end' at position {self.peek().position}")
            self.advance()
        
        elif token.type == TOKEN_SAVE:
            # save - save memory state to disk
            self.advance()  # Consume 'save'
            self.emit_byte(OP_SAVE_FILE)
        
        elif token.type == TOKEN_LOAD:
            # load - load memory state from disk
            self.advance()  # Consume 'load'
            self.emit_byte(OP_LOAD_FILE)
        
        elif token.type == TOKEN_PRINT:
            # print/imprimir expression
            self.advance()  # Consume 'print' or 'imprimir'
            self.parse_expression()
            self.emit_byte(OP_PRINT)
        
        elif token.type == TOKEN_IDENTIFIER:
            # Check if this is actually a print statement with 'imprimir' that wasn't caught by lexer
            # (defensive programming - should not happen if lexer is correct, but provides safety)
            if token.value == 'imprimir' or token.value == 'print':
                # This should not happen if lexer works correctly, but handle it gracefully
                self.advance()  # Consume keyword
                self.parse_expression()
                self.emit_byte(OP_PRINT)
            else:
                # variable <- expression
                var_name = self.advance().value
                var_index = self.get_var_index(var_name)
                
                if self.peek().type != TOKEN_ARROW:
                    raise SyntaxError(f"Expected '<-' after identifier '{var_name}' at position {self.peek().position}")
                
                self.advance()  # Consume '<-'
                self.parse_expression()
                self.emit_byte(OP_STORE)
                self.emit_int(var_index)
        
        else:
            raise SyntaxError(f"Unexpected token {token.type} at position {token.position}")
    
    def parse(self) -> List[int]:
        """Parse the entire program."""
        while self.peek().type != TOKEN_EOF:
            self.parse_statement()
        
        self.emit_byte(OP_HALT)
        return self.bytecode


def compile_picolin(source: str) -> bytes:
    """
    Compile Picolin source code to bytecode.
    
    Args:
        source: Picolin source code string
    
    Returns:
        bytes: Binary bytecode ready to write to file
    """
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    
    parser = Parser(tokens)
    bytecode = parser.parse()
    
    return bytes(bytecode)


def compile_file(input_file: str, output_file: str = "program.bin"):
    """
    Compile a Picolin source file to bytecode file.
    
    Args:
        input_file: Path to Picolin source file
        output_file: Path to output bytecode file
    """
    try:
        with open(input_file, 'r') as f:
            source = f.read()
        
        bytecode = compile_picolin(source)
        
        with open(output_file, 'wb') as f:
            f.write(bytecode)
        
        print(f"Compilation successful: {input_file} -> {output_file}")
        print(f"Bytecode size: {len(bytecode)} bytes")
    
    except Exception as e:
        print(f"Compilation error: {e}")
        raise


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python compiler.py <input.picolin> [output.bin]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "program.bin"
    
    compile_file(input_file, output_file)
