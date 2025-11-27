from lark import Lark, Token, Transformer, Tree

# simple C-like grammar for LLVM testing

GRAMMAR = """

start: (statement)+
?block_statement: function_def

?expression: expression "+" term -> add
    | expression





"""
