from typing import Any, Dict, List, Union, assert_never

from lark import Lark, Token, Transformer, Tree, Visitor
from lark.visitors import Interpreter
from llvmlite import ir

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


class IRTransformer(Transformer):
    def __init__(self):
        self.module = ir.Module(name="module")

    def call(self, items) -> ir.FunctionType:
        print("CALL:", items, type(items))
        return items

    def dimensions(self, items: List[Token]):
        print("DIMENSIONS:", items, type(items), type(items[0]))
        acc = []
        for item in items:
            acc.append(int(item.value))
        return acc

    def atom(self, items) -> Union[ir.Constant, ir.AllocaInstr]:
        print("ATOM:", items, type(items))
        match items:
            case [Token("FLOAT", value)]:
                return ir.Constant(ir.FloatType(), float(value))
            case [Token("INT", value)]:
                return ir.Constant(ir.IntType(32), int(value))
            case [Token("NAME", value)]:
                return ir.AllocaInstr(value, ir.IntType(32), 1, name=value)
            case _:
                assert_never(items)


class LLVMInterpreter(Interpreter):
    def __init__(self):
        super().__init__()
        self.module = ir.Module(name="module")
        self.context_stack: List[Dict[str, Any]] = []
        self.current_function = None
        self.current_block = None
        self.block_counter = 0

    def push_context(self, context):
        # TODO
        pass

    def pop_context(self):
        if self.context_stack:
            prev_context = self.context_stack.pop()
            self.current_function = prev_context["current_function"]
            self.current_block = prev_context["current_block"]

    def function_def(self, tree: Tree[Token]):
        print("function definition:", tree)
        self.current_function = tree.children[1].value
        self.visit_children(tree)

    def block(self, tree: Tree[Token]):
        print("block:", tree)
        self.current_block = f"block_{self.block_counter}"
        self.push_context(
            {
                "current_function": self.current_function,
                "current_block": self.current_block,
            }
        )
        self.visit_children(tree)


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
