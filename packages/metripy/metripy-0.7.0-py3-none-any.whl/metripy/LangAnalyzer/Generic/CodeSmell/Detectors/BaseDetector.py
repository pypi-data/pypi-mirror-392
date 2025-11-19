"""Generic base detector for code smells across languages"""

from abc import ABC, abstractmethod
from typing import List

from metripy.Application.Config.CodeSmellConfig import CodeSmellConfig
from metripy.LangAnalyzer.Generic.CodeSmell.AstParser import AstParser
from metripy.LangAnalyzer.Generic.CodeSmell.CodeSmell import CodeSmell


class BaseCodeSmellDetector(ABC):
    """Base class for language-agnostic code smell detectors"""

    def __init__(self, filename: str, parser: AstParser, config: CodeSmellConfig):
        """
        Initialize detector with a language-specific parser.

        Args:
            filename: Path to the file being analyzed
            parser: Language-specific AST parser (already parsed)
        """
        self.filename = filename
        self.parser = parser
        self.smells: List[CodeSmell] = []
        self.config = config

    @abstractmethod
    def detect(self) -> List[CodeSmell]:
        """Detect code smells and return a list of CodeSmell objects"""
        pass

    def get_line_number(self, node) -> int:
        """Get line number from tree-sitter node"""
        return node.start_point[0] + 1  # tree-sitter uses 0-based indexing

    def get_column(self, node) -> int:
        """Get column number from tree-sitter node"""
        return node.start_point[1]

    def get_end_line(self, node) -> int:
        """Get end line number from tree-sitter node"""
        return node.end_point[0] + 1
