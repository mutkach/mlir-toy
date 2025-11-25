# LLVM IR Code Generation with Python

An exploratory project for learning LLVM IR generation using Python's `llvmlite` bindings and Lark parser.

## Project Structure

- **`simple_ir.py`** - Manual IR construction using llvmlite. Demonstrates linear IR building for simple functions and includes optimization passes.

- **`main.c`** - Equivalent C code for comparison. Compile with `clang -S -emit-llvm main.c` to examine the generated IR.

- **`parser.py`** - Exploration of AST-driven IR generation using Lark's `Transformer` and `Interpreter` patterns. Currently a draft implementation.

- **`grammar.lark`** - Lark grammar definition for the toy language, supporting basic arithmetic, variables, and function definitions.

## Purpose

This is a learning project to understand:
- LLVM IR structure and generation
- AST parsing with Lark
- Different approaches to code generation (manual vs. AST-driven)
