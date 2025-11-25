# we want to test a few files and see the AST
from parser import Parser


# test 1:
def test_parser():
    parser = Parser("grammar.lark")
    with open("test1.toy") as file:
        code = file.read()
    tree = parser.parse(code)
    print(tree.pretty())
    assert tree is not None


test_parser()
