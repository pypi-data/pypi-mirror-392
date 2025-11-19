from abc import ABC, abstractmethod
from typing import Dict

from tree_sitter import Node


class GenericCognitiveComplexityCalculator(ABC):
    def __init__(self, parser):
        self.parser = parser
        self.language = parser.language
        self.node_map = self.get_node_map()

    def calculate_for_function(self, function_node: Node) -> int:
        return self._calculate_recursive(
            function_node, nesting=0, in_else_if_chain=False
        )

    @abstractmethod
    def get_node_map(self) -> Dict[str, str]:
        pass

    def _calculate_recursive(
        self, node: Node, nesting: int, in_else_if_chain: bool
    ) -> int:
        complexity = 0

        # Handle if-statements with else-if chains
        if node.type == self.node_map.get("if"):
            complexity += 1 + (nesting if not in_else_if_chain else 0)

            # Check for else-if chain
            for child in node.children:
                if child.type == self.node_map.get("else"):
                    inner_if = next(
                        (
                            c
                            for c in child.children
                            if c.type == self.node_map.get("if")
                        ),
                        None,
                    )
                    if inner_if:
                        complexity += self._calculate_recursive(
                            inner_if, nesting, in_else_if_chain=True
                        )

            nesting += 1

        elif node.type == self.node_map.get("switch"):
            complexity += 1 + nesting
            nesting += 1  # Cases do NOT add nesting penalty

        elif node.type in [
            self.node_map.get("for"),
            self.node_map.get("while"),
            self.node_map.get("try"),
            self.node_map.get("catch"),
            self.node_map.get("except"),
        ]:
            complexity += 1 + nesting
            nesting += 1

        # Traverse children (skip else-if handled above)
        for child in node.children:
            if node.type == self.node_map.get("if") and child.type == self.node_map.get(
                "else"
            ):
                continue
            complexity += self._calculate_recursive(
                child, nesting, in_else_if_chain=False
            )

        return complexity

    def calculate_for_all_functions(self) -> Dict[str, int]:
        results = {}
        for func_node in self.parser.get_function_nodes():
            func_name = self.parser.extract_function_name(func_node) or "<anonymous>"
            results[func_name] = self.calculate_for_function(func_node)
        return results
