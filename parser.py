import enum
from typing import Any, Dict, List, Union, assert_never

from lark import Lark, Token, Transformer, Tree, Visitor
from lark.visitors import Interpreter
from llvmlite import ir
from llvmlite.ir.types import BaseStructType
from pydantic import BaseModel

GRAMMAR = """
%import common.INT
%import common.FLOAT
%import common.CNAME -> NAME // This is a standard and robust definition for NAME
%import common.WS
%import common.C_COMMENT

// --- Ignoring ---
%ignore WS          // Ignore whitespace (spaces, tabs, and newlines!)
%ignore C_COMMENT   // Also ignore C-style comments (/* ... */)
?start: statement*

?statement: simple_statement ";"
          | block_statement

?simple_statement: definition
                 | expression

?block_statement: function_def

?expression: expression "+" term   -> add
    | expression "-" term   -> sub
    | "return" expression -> return_stmt
    | term

?term : term "*" factor   -> mul
    | term "/" factor   -> div
    | factor

?factor: num_atom

?block: "{" statement* "}"

?dimensions: "<" INT ("," INT)* ">" -> dimensions

?definition: "var" NAME "=" expression  -> var_def
    | "var" NAME dimensions "=" expression  -> array_def


?function_def: "def" NAME "(" [NAME ("," NAME)*] ")" block

?num_atom: atom
    | "-" num_atom       -> neg
    | "+" num_atom       -> pos
    | call -> call_expr
    | "(" expression ")"
    | NAME

?call: NAME "(" [expression ("," expression)*] ")"

?list: "[" expression ("," expression)*  "]"

?atom: FLOAT
    | INT
    | NAME
    | list
"""



type TypedAST = Union[Tree[BaseStructType], Token]



class TypeChecker(Visitor):

    def __init__(self):
        super().__init__()




class Parser:
    def __init__(self, grammar_path: str | None):
        if grammar_path:
            with open(grammar_path, "r") as file:
                file_content = file.read()
            self.parser = Lark(file_content)
        else:
            self.parser = Lark(GRAMMAR)
        self.compiler = LLVMInterpreter()

    def parse(self, code: str):
        ast = self.parser.parse(code)
        ir = self.compiler.visit(ast)
        return self.parser.parse(code)
