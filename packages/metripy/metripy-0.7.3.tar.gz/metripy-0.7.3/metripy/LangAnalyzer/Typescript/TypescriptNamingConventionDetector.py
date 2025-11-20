"""TypeScript-specific naming convention detector"""

from typing import Dict

from metripy.LangAnalyzer.Generic.CodeSmell.CodeSmell import (
    CodeSmellSeverity,
    CodeSmellType,
)
from metripy.LangAnalyzer.Generic.CodeSmell.Detectors.NamingConventionDetector import (
    NamingConventionDetector,
)


class TypescriptNamingConventionDetector(NamingConventionDetector):
    """TypeScript-specific naming convention detector"""

    def _get_naming_rules(self) -> Dict[str, Dict]:
        return {
            "class": {
                "pattern": r"^[A-Z][a-zA-Z0-9]*$",
                "description": "PascalCase",
                "smell_type": CodeSmellType.PASCAL_CASE_VIOLATION_CLASS,
                "severity": CodeSmellSeverity.MINOR,
                "excludes": [],
            },
            "function": {
                "pattern": r"^[a-z][a-zA-Z0-9]*$",
                "description": "camelCase",
                "smell_type": CodeSmellType.SNAKE_CASE_VIOLATION_FUNCTION,
                "severity": CodeSmellSeverity.MINOR,
                "excludes": [
                    r"^_",  # Private methods
                ],
            },
            "variable": {
                "pattern": r"^[a-z][a-zA-Z0-9]*$",
                "description": "camelCase",
                "smell_type": CodeSmellType.SNAKE_CASE_VIOLATION_VARIABLE,
                "severity": CodeSmellSeverity.INFO,
                "excludes": [
                    r"^_",  # Private variables
                ],
            },
            "constant": {
                "pattern": r"^[A-Z][A-Z0-9_]*$",
                "description": "SCREAMING_SNAKE_CASE",
                "smell_type": CodeSmellType.SCREAMING_SNAKE_CASE_VIOLATION_CONSTANT,
                "severity": CodeSmellSeverity.MINOR,
                "excludes": [],
            },
        }
