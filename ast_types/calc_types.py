from typing import Any, List, Literal, Tuple, Union

from pydantic import BaseModel, Field, field_serializer
from pydantic.functional_validators import model_validator


class TokenInfo(BaseModel):
    span: Tuple[int | None, int | None]
    line: Union[int, None]

class TypeSerializableModel(BaseModel):
    token_info: TokenInfo

    @field_serializer('value_type', mode='plain', check_fields=False)
    def serialize_types(self, value: type) -> str:
        if isinstance(value, type):
            return value.__name__
        return str(value)

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        if 'token_info' in data:
            token_info = data.pop('token_info', None)
            data['token_info'] = token_info
        return data

class ConjunctionOp(TypeSerializableModel):
    '''
        rule description
        ?conjunction: inversion ("and" inversion )*
    '''
    inversions: List[bool]
    value_type: type = Field(default=bool)

    def execute(self) -> bool:
        return all(self.inversions)


class DisjunctionOp(TypeSerializableModel):
    '''
        rule description
        ?disjunction: conjunction ("or" conjunction )*
    '''
    conjunctions: List[bool]
    value_type: type = Field(default=bool)

    def execute(self) -> bool:
        return any(self.conjunctions)


class InversionOp(TypeSerializableModel):
    sign: Literal['not', '']
    value: bool
    value_type: type = Field(default=bool)
    def execute(self) -> bool:
        if self.sign == 'not':
            return not self.value
        return self.value


class CondOp(TypeSerializableModel):
    _if: bool
    _then: Any
    _else: Any
    value_type: type = Field(default=bool)
    # may not be necessary depending on usage
    @model_validator(mode='after')
    def fields_match_type(self):
        if type(self._then) is not type(self._else):
            raise ValueError('field1 and field2 must be the same type')
        return self

    def execute(self) -> Any:
        if self._if:
            return self._then
        return self._else

class ArithOp(TypeSerializableModel):
    arith_kind: Literal['+', '-', '*', '/']
    left: Any
    right: Any
    value_type: type = Field(default=int)

    #def execute(self) -> Union[int, float]:
    #    match self.arith_kind:
    #        case '+':
    #            return self.left + self.right
    #        case '-':
    #            return self.left - self.right
    #        case '*':
    #            return self.left * self.right
    #        case '/':
    #            return self.left / self.right
    #        case _:
    #            raise ValueError(f'Unknown arithmetic operation: {self.arith_type}')

class CompOp(TypeSerializableModel):
    comp_type: Literal['==', '!=', '<', '>', '<=', '>=']
    left: Union[int, float]
    right: Union[int, float]
    value_type: type = Field(default=bool)

    def execute(self) -> bool:
        match self.comp_type:
            case '==':
                return self.left == self.right
            case '!=':
                return self.left != self.right
            case '<':
                return self.left < self.right
            case '>':
                return self.left > self.right
            case '<=':
                return self.left <= self.right
            case '>=':
                return self.left >= self.right
            case _:
                raise ValueError(f'Unknown comparison operation: {self.comp_type}')

class UnaryOp(TypeSerializableModel):
    sign: Literal['+', '-']
    value: Union[int, float]
    value_type: type = Field(default=int)

    def execute(self) -> Union[int, float]:
        if self.sign == '-':
            return -self.value
        else:
            return self.value


class Atom(TypeSerializableModel):
    value: Union[int, float, str, bool]
    value_type: type = Field(...)

    def execute(self) -> Union[int, float, str, bool]:
        return self.value

type ExpressionType = Union[Atom, UnaryOp, CompOp, ArithOp,
    CondOp, InversionOp, DisjunctionOp, ConjunctionOp]
