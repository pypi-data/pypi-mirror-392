import ast
from abc import ABC, abstractmethod
from typing import List, Set

from metripy.LangAnalyzer.Generic.CodeSmell import CodeSmell


class BaseCodeSmellDetector(ABC):
    """Base class for all code smell detectors"""

    def __init__(self, filename: str, code: str, tree: ast.AST | None = None):
        self.filename = filename
        self.code = code
        self.tree = tree
        self.smells: List[CodeSmell] = []

    @abstractmethod
    def detect(self) -> List[CodeSmell]:
        """Detect code smells and return a list of CodeSmell objects"""
        pass

    def _get_used_names(self) -> Set[str]:
        """Get all names that are used (loaded) in the code"""
        used_names = set()

        if not self.tree:
            return used_names

        for node in ast.walk(self.tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                # For attribute access like 'module.function', track 'module'
                if isinstance(node.value, ast.Name):
                    used_names.add(node.value.id)
                    used_names.add(f"{node.value.id}.{node.attr}")

        return used_names
