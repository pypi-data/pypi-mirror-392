"""Generic AST parser using tree-sitter for multiple languages"""

from abc import ABC, abstractmethod
from typing import List, Optional

from tree_sitter import Node, Tree
from tree_sitter_languages import get_parser


class AstParser(ABC):
    """Base class for language-agnostic AST parsing using tree-sitter"""

    def __init__(self, language: str):
        """
        Initialize parser for a specific language.

        Args:
            language: Language name (e.g., 'python', 'typescript', 'php')
        """
        self.language = language
        self.parser = get_parser(language)
        self.tree: Optional[Tree] = None
        self.code: str = ""

    def parse(self, code: str) -> Optional[Tree]:
        """Parse code and return tree-sitter tree"""
        self.code = code
        try:
            self.tree = self.parser.parse(bytes(code, "utf8"))
            return self.tree
        except Exception:
            return None

    def get_node_text(self, node: Node) -> str:
        """Get the text content of a node"""
        if not self.code:
            return ""
        return node.text.decode("utf-8")
        # return self.code[node.start_byte : node.end_byte]

    def find_nodes_by_type(
        self, node_type: str, root: Optional[Node] = None
    ) -> List[Node]:
        """Find all nodes of a specific type"""
        if root is None:
            if self.tree is None:
                return []
            root = self.tree.root_node

        nodes = []
        self._find_nodes_recursive(root, node_type, nodes)
        return nodes

    def _find_nodes_recursive(
        self, node: Node, node_type: str, results: List[Node]
    ) -> None:
        """Recursively find nodes of a specific type"""
        if node.type == node_type:
            results.append(node)

        for child in node.children:
            self._find_nodes_recursive(child, node_type, results)

    def walk_tree(self, node: Optional[Node] = None):
        """Generator to walk through all nodes in the tree"""
        if node is None:
            if self.tree is None:
                return
            node = self.tree.root_node

        yield node
        for child in node.children:
            yield from self.walk_tree(child)

    @abstractmethod
    def get_import_nodes(self) -> List[Node]:
        """Get all import nodes (language-specific)"""
        pass

    @abstractmethod
    def get_function_nodes(self) -> List[Node]:
        """Get all function/method definition nodes (language-specific)"""
        pass

    @abstractmethod
    def get_class_nodes(self) -> List[Node]:
        """Get all class definition nodes (language-specific)"""
        pass

    @abstractmethod
    def get_variable_assignment_nodes(self) -> List[Node]:
        """Get all variable assignment nodes (language-specific)"""
        pass

    @abstractmethod
    def get_identifier_nodes(self, context: str = "usage") -> List[Node]:
        """
        Get identifier nodes based on context.

        Args:
            context: 'usage' for variable usage, 'definition' for declarations
        """
        pass

    @abstractmethod
    def extract_function_name(self, node: Node) -> Optional[str]:
        """Extract function name from a function definition node"""
        pass

    @abstractmethod
    def extract_class_name(self, node: Node) -> Optional[str]:
        """Extract class name from a class definition node"""
        pass

    @abstractmethod
    def extract_variable_name(self, node: Node) -> Optional[str]:
        """Extract variable name from an assignment node"""
        pass

    @abstractmethod
    def extract_import_name(self, node: Node) -> Optional[str]:
        """Extract imported name from an import node"""
        pass

    @abstractmethod
    def get_function_parameters(self, function_node: Node) -> List[str]:
        """Extract parameter names from a function definition"""
        pass

    def get_code_line(self, node: Node) -> str:
        """Get the code line from a node"""
        return self.code[node.start_byte : node.end_byte]
