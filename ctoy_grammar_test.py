from lark import Lark, Tree, Transformer, Visitor, Token
from lark.visitors import Interpreter
from llvmlite import binding as llvm
from llvmlite import ir
from typing import List, Sequence, Dict, Tuple, TypeVar, Generic, Any, Union
from dataclasses import dataclass


@dataclass
class Type:
    pass

@dataclass
class IntType(Type):
    pass
T = TypeVar('T', bound=Type)

@dataclass
class ArrayType(Generic[T], Type):
    element_type: T
    dimensions: List[int]

@dataclass
class TypedValue(Generic[T]):
    """A value paired with its DSL type"""
    type: Type
    value: T

class Op:
    pass

@dataclass
class AddOp(Type):
    left: TypedValue[Any]
    right: TypedValue[Any]

# A simple compiler that builds an IR from the parse tree

# we need types before building the IR
class CtoyCompiler(Transformer):
    def __init__(self):
        self.context: Dict[str, TypedValue[Any]] = {}
        self.module = ir.Module(name="ctoy_module")

    def NAME(self, token: Token) -> str:
        return str(token)

    def dimensions(self, items: List[Token]) -> List[int]:
        return [int(item.value) for item in items]

    def list(self, items: List[Token]) -> List[int]:
        print("list items:", items)
        return [int(item.value) for item in items]

    def array_def(self, items: List[Tree]) -> TypedValue[Any]:
        var_name = items[0]
        dimensions = items[1]  # assuming second item is the dimensions
        values = items[-1]  # assuming last item is the list of values
        element_type = IntType()  # assuming integer arrays for simplicity
        array_type = ArrayType(element_type, [dimensions])  # only handling 1D for simplicity
        self.context[var_name] = TypedValue(type=array_type, value=values)
        return TypedValue(type=array_type, value=values)  # Placeholder

    def add(self, items: List[Union[str, TypedValue[Any]]]) -> AddOp:
        left, right = items
        left.type = self.context.get(left, None)
        
        assert isinstance(left.type, ArrayType) and isinstance(right.type, ArrayType)
        assert left.type.size == right.type.size
        # Placeholder for actual addition logic
        return TypedValue(type=left.type, value=None)


lark = Lark.open("./grammars/ctoy.lark")
code = '''
var a <10> = [1,2,3,4,5,6,7,8,9,10];
var b <10> = [1,2,3,4,5,6,7,8,9,10];
return a + b;
'''
tree = lark.parse(code)
print(tree.pretty())
cc = CtoyCompiler()
typed_tree = cc.transform(tree)
print(typed_tree)
