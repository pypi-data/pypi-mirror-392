"""
Python code smell detector - wrapper around the generic tree-sitter-based detector.

For backward compatibility, this provides the same interface as before.
Now uses the generic GenericCodeSmellDetector framework.
"""

from typing import List

from metripy.Application.Config.CodeSmellConfig import CodeSmellConfig
from metripy.LangAnalyzer.Generic.CodeSmell.CodeSmell import CodeSmell
from metripy.LangAnalyzer.Generic.CodeSmell.GenericCodeSmellDetector import (
    GenericCodeSmellDetector,
)


class PythonCodeSmellDetector:
    """
    Python code smell detector using tree-sitter-based generic framework.

    This is a convenience wrapper that maintains backward compatibility.
    For direct access, use: GenericCodeSmellDetector.for_python()
    """

    def __init__(self, config: CodeSmellConfig):
        self.config = config

    def detect_all(self, filename: str, code: str) -> List[CodeSmell]:
        """Run all configured code smell detection checks"""
        detector = GenericCodeSmellDetector.for_python(self.config, filename, code)
        return detector.detect_all()
