from typing import Dict
from tree_sitter import Node
from metripy.LangAnalyzer.Generic.Ast.AstParser import AstParser
import math

class HalsteadAnalyzer:
    def __init__(self, parser: AstParser):
        self.parser = parser
        self.operators = []
        self.operands = []

    def analyze(self) -> Dict[str, float]:
        self._collect_tokens(self.parser.tree.root_node)

        n1 = len(set(self.operators))
        n2 = len(set(self.operands))
        N1 = len(self.operators)
        N2 = len(self.operands)

        n = n1 + n2
        N = N1 + N2
        V = N * (0 if n == 0 else (math.log2(n)))
        D = (n1 / 2) * (N2 / n2 if n2 else 0)
        E = D * V

        return {
            "n1": n1, "n2": n2, "N1": N1, "N2": N2,
            "Vocabulary": n, "Length": N,
            "Volume": V, "Difficulty": D, "Effort": E
        }

    def _collect_tokens(self, node: Node):
        # Language-specific classification
        if node.type in self.parser.get_operator_types():
            self.operators.append(self.parser.get_node_text(node))
        elif node.type in self.parser.get_operand_types():
            self.operands.append(self.parser.get_node_text(node))

        for child in node.children:
            self._collect_tokens(child)