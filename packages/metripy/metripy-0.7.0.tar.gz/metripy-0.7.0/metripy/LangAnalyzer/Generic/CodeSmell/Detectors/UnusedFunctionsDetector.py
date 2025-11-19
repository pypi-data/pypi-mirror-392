"""Generic detector for unused functions across languages"""

from typing import List, Set

from metripy.LangAnalyzer.Generic.CodeSmell.CodeSmell import (
    CodeSmell,
    CodeSmellSeverity,
    CodeSmellType,
)
from metripy.LangAnalyzer.Generic.CodeSmell.Detectors.BaseDetector import (
    BaseCodeSmellDetector,
)


class UnusedFunctionsDetector(BaseCodeSmellDetector):
    """Detects unused private functions in any language"""

    def detect(self) -> List[CodeSmell]:
        """Detect unused private functions"""
        function_nodes = self.parser.get_function_nodes()
        if not function_nodes:
            return []

        # Track private function definitions
        private_functions = {}  # name -> node
        called_functions = self._get_called_functions()

        for func_node in function_nodes:
            func_name = self.parser.extract_function_name(func_node)
            if not func_name:
                continue

            # Check if it's a private function (starts with _ in Python, TypeScript convention)
            if self._is_private_function(func_name):
                private_functions[func_name] = func_node

        # Find unused private functions
        for func_name, func_node in private_functions.items():
            if func_name not in called_functions:
                self.smells.append(
                    CodeSmell(
                        smell_type=CodeSmellType.UNUSED_FUNCTION,
                        severity=CodeSmellSeverity.MINOR,
                        filename=self.filename,
                        line_number=self.get_line_number(func_node),
                        column=self.get_column(func_node),
                        end_line=self.get_end_line(func_node),
                        code_line=self.parser.get_code_line(func_node),
                        message=f"Unused private function '{func_name}'",
                        symbol=func_name,
                    )
                )

        return self.smells

    def _is_private_function(self, name: str) -> bool:
        """Check if function name indicates it's private"""
        # Python/TypeScript convention: starts with _ but not __
        if name.startswith("_") and not name.startswith("__"):
            return True
        # TypeScript might also use # for private
        if name.startswith("#"):
            return True
        return False

    def _get_called_functions(self) -> Set[str]:
        """Get all function names that are called in the code"""
        called = set()

        # Get all identifiers that could be function calls
        identifiers = self.parser.get_identifier_nodes("usage")

        for identifier in identifiers:
            name = self.parser.get_node_text(identifier)
            if name:
                called.add(name)

        return called
