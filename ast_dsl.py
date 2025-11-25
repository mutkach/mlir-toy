from typing import Callable, Union, Any
import lark
import json

GRAMMAR_TEMPLATE: Callable[[list[str], list[str]], str] = (
    lambda list_of_variables, list_of_functions: f"""
?start: expression
?expression: atom
    | expression 
    | arith
    | comparison
    | conditional
    | disjunction
                   
?disjunction: conjunction ("or" conjunction )+ 
    | conjunction

?conjunction: inversion ("and" inversion )+ 
    | inversion

?inversion: "not" inversion 
    | comparison

?conditional: "if" expression "then" expression "else" expression "end"
                   
?list: "[" expression ("," expression)*  "]"

?comparison: arith
    | arith "==" arith -> comp_eq
    | arith "!=" arith -> comp_ne
    | arith "<" arith -> comp_lt
    | arith "<=" arith -> comp_le
    | arith ">" arith -> comp_gt
    | arith ">=" arith -> comp_ge
    | arith "in" arith -> comp_in
    | arith "not" "in" arith -> comp_not_in


                   
?arith: product
    | arith "+" product -> add
    | arith "-" product -> sub
                   

?product: num_atom
    | product "*" num_atom -> mult
    | product "/" num_atom -> div
                   

?num_atom: atom
    | negation
    | call
    | VARIABLE
    | "(" expression ")"

negation: "-" num_atom

call: FUNC "(" [arguments] ")"

?arguments: expression ("," expression)*

?numeric: FLOAT
    | INT
                   
?atom: DATETIME
    | TIME
    | DATE
    | PERIOD
    | TIMEZONE
    | FLOAT
    | INT
    | STRING
    | VARIABLE
    | BOOL
    | NONE
    | list




//VARIABLE: /(?!(?:and|or|if|then|else|end)\b)[_a-zA-Z][_a-zA-Z0-9]*/
                   
FUNC: /{"|".join(list_of_functions + ['default_func'])}/
VARIABLE: /{"|".join(list_of_variables + ['default_name'])}/
                   
DIGIT: /[0-9]/
FLOAT: /[0-9]+\.[0-9]+/
INT: /\\-?0|[1-9][0-9]*/
BOOL: /True|False/
DATETIME: "DT" STRING 
DATE: "D" STRING 
TIME: "T" STRING 
TIMEZONE: "TZ" STRING 
PERIOD: "P" STRING 
NONE: "None"

%import common.WS_INLINE
%import python.STRING
%ignore WS_INLINE
%import common.WS
%ignore WS
"""
)


class StripPrefixes(lark.Transformer[lark.Token, lark.Token]):
    def DATETIME(self, token: lark.Token) -> lark.Token:
        return token.update(value=token.value[3:-1])  # Remove "DT"
    
    def DATE(self, token: lark.Token) -> lark.Token:
        return token.update(value=token.value[2:-1])  # Remove "D"
    
    def TIME(self, token: lark.Token) -> lark.Token:
        return token.update(value=token.value[2:-1])  # Remove "T"
    
    def TIMEZONE(self, token: lark.Token) -> lark.Token:
        return token.update(value=token.value[3:-1])  # Remove "TZ"
    
    def PERIOD(self, token: lark.Token) -> lark.Token:
        return token.update(value=token.value[2:-1])  # Remove "P"

class Parser:

    def __init__(self, variables: list[str], functions: list[str]):
        """
        Initializes the AST DSL parser with the provided variables and
        functions.

        Args:
            variables (list[str]): A list of variable names 
                                   to be included in the grammar.
            functions (list[str]): A list of function names 
                                   to be included in the grammar.

        The variables and functions are sorted by length in 
        descending order before being used to generate the grammar 
        (in case some variables are substrings of other variables).
        """
        self.grammar = GRAMMAR_TEMPLATE(
            sorted(variables, key=lambda x: len(x), reverse=True),
            sorted(functions, key=lambda x: len(x), reverse=True),
        )

        self.transformer = StripPrefixes()
        self.parser = lark.Lark(self.grammar)

    def tree_to_json(self, tree: lark.Tree[str]) -> dict[str, str]:
        """Convert a Lark tree to JSON string."""
        tree_dict = self._tree_to_dict(tree)
        return tree_dict

    def _tree_to_dict(
        self,
        item: Union[lark.Tree[str], lark.Token, str]
    ) -> dict[str, Any]:
        """Recursively convert tree/token to a dictionary."""
        if isinstance(item, lark.Tree):
            return {
                "type": item.data,
                "children":
                    [self._tree_to_dict(child) for child in item.children]
            }
        elif isinstance(item, lark.Token):
            return {
                "type": item.type,
                "text": str(item),  # Token value as-is
                "line": item.line,
                "column": item.column
            }
        else:
            # Handle plain strings if they appear
            return {"type": "literal", "value": item}

    def parse(
        self,
        condition_str: str
    ) -> Union[lark.Tree[lark.Token], lark.Token]:
        """
        Parse a condition string following the rules of the grammar into an AST
        """
        ast = self.parser.parse(condition_str)
        stripped_ast = self.transformer.transform(ast)
        return stripped_ast
