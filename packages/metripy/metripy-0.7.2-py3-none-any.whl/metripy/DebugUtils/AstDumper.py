from tree_sitter import Node

from metripy.LangAnalyzer.Generic.Ast.AstParser import AstParser
from metripy.LangAnalyzer.Python.Ast.PythonAstParser import PythonAstParser


class AstDumper:
    def __init__(self, parser: AstParser):
        self.parser = parser

    def dump_all(self):
        self.dump(self.parser.tree.root_node)

    def dump(self, node: Node, depth: int = 0):
        print(" " * depth + node.type + " | " + self.parser.get_node_text(node))
        for child in node.children:
            self.dump(child, depth + 1)


if __name__ == "__main__":
    parser = PythonAstParser()
    with open("metripy/Git/GitAnalyzer.py", "r") as file:
        code = file.read()
    parser.parse(code)
    dumper = AstDumper(parser)
    dumper.dump_all()
