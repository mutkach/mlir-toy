from typing import Any, List, Literal, Tuple, Union, assert_never

from lark import Lark, Token, Transformer, Tree, Visitor
from lark.visitors import InlineTransformer
from pydantic import BaseModel, Field

from ast_types.calc_types import (
    ArithOp,
    Atom,
    CondOp,
    ConjunctionOp,
    DisjunctionOp,
    ExpressionType,
    InversionOp,
    TokenInfo,
)


class ParseException(Exception):
    def __init__(self, message: str):
        super().__init__(message)

class TypeTransformer(Transformer):
    def __init__(self):
        super().__init__()

    def start(self, items: List[Any]) -> Any:
        # Returns the single root node (the result of 'expression')
        assert len(items) == 1
        return items[0]

    def expression(self, items: List[Any]) -> Any:
        # Returns the single node that was matched (arith, atom, comparison, etc.)
        assert len(items) == 1
        return items[0]

    def BOOL(self, item: Token) -> Atom:
        token_info = TokenInfo(
            span=(item.column, item.end_column),
            line=item.line
        )
        return Atom(value=bool(item.value), value_type=bool, token_info=token_info)

    def INT(self, item: Token) -> Atom:
        token_info = TokenInfo(
            span=(item.column, item.end_column),
            line=item.line
        )
        return Atom(value=int(item.value), value_type=int, token_info=token_info)

    def FLOAT(self, item: Token) -> Atom:
        token_info = TokenInfo(
            span=(item.column, item.end_column),
            line=item.line
        )
        return Atom(value=float(item.value), value_type=float, token_info=token_info)

    def arith(self, items: List[Any]) -> ArithOp:
        assert len(items) == 3
        left, op, right = items
        token_info = TokenInfo(
            span=(op.column, op.end_column),
            line=op.line
        )
        left_type, right_type = left.value_type, right.value_type
        operator = op.value
        match (left_type, right_type):
            case _ if left_type not in [float, int]:
                raise ParseException(f"Type mismatch in arithmetic operation: {left_type} {left.token_info}")
            case _ if right_type not in [float, int]:
                raise ParseException(f"Type mismatch in arithmetic operation: {left_type} {right.token_info}")
            case _ if left_type is float or right_type is float:
                return ArithOp(
                    left=left,
                    right=right,
                    arith_kind=operator,
                    value_type=float,
                    token_info=token_info
                )
            case _ if left_type is right_type is int:
                return ArithOp(
                    left=left,
                    right=right,
                    arith_kind=operator,
                    value_type=int,
                    token_info=token_info
                )
            case _:
                raise ParseException(f"Type mismatch in arithmetic operation: {token_info}")



    def product(self, items: List[Any]) -> ArithOp:
        assert len(items) == 3
        left, op, right = items
        token_info = TokenInfo(
            span=(op.column, op.end_column),
            line=op.line
        )
        left_type, right_type = left.value_type, right.value_type
        operator = op.value
        match (left_type, op, right_type):
            case _, '*', _ if left_type is right_type is int:
                return ArithOp(
                    left=left,
                    right=right,
                    arith_kind=operator,
                    value_type=int,
                    token_info=token_info,
                )
            case _, _, _ if left_type in [int, float] and right_type in [int, float]:
                return ArithOp(
                    left=left,
                    right=right,
                    arith_kind=operator,
                    value_type=float,
                    token_info=token_info,
                )
            case _:
                raise ParseException(f"Type mismatch in arithmetic operation: {left.token_info} {right.token_info}")

    def inversion(self, items: List[Any]) -> InversionOp:
        assert len(items) == 2
        _not, invertable = items
        token_info = TokenInfo(
            span=(_not.column, _not.end_column),
            line=_not.line
        )
        match _not:
            case Token(value='not'):
                return InversionOp(
                    sign='not',
                    value= invertable.value,
                    value_type=bool,
                    token_info=token_info,
                )
            case _:
                assert_never(_not)
