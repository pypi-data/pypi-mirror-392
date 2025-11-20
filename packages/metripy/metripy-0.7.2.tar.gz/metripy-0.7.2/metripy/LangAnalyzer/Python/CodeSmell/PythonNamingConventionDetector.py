"""Python-specific naming convention detector (PEP 8)"""

from typing import Dict

from metripy.LangAnalyzer.Generic.CodeSmell.CodeSmell import (
    CodeSmellSeverity,
    CodeSmellType,
)
from metripy.LangAnalyzer.Generic.CodeSmell.Detectors.NamingConventionDetector import (
    NamingConventionDetector,
)


class PythonNamingConventionDetector(NamingConventionDetector):
    """Python-specific naming convention detector (PEP 8)"""

    def _get_naming_rules(self) -> Dict[str, Dict]:
        return {
            "class": {
                "pattern": self.PATTERN_PASCAL_CASE,
                "description": "PascalCase",
                "smell_type": CodeSmellType.PASCAL_CASE_VIOLATION_CLASS,
                "severity": CodeSmellSeverity.MINOR,
                "excludes": [],
            },
            "function": {
                "pattern": self.PATTERN_SNAKE_CASE,
                "description": "snake_case",
                "smell_type": CodeSmellType.SNAKE_CASE_VIOLATION_FUNCTION,
                "severity": CodeSmellSeverity.MINOR,
                "excludes": [
                    r"^__.*__$",  # Magic methods like __init__
                    r"^_",  # Private methods
                    r"^test_",  # Test methods
                ],
            },
            "variable": {
                "pattern": self.PATTERN_SNAKE_CASE,
                "description": "snake_case",
                "smell_type": CodeSmellType.SNAKE_CASE_VIOLATION_VARIABLE,
                "severity": CodeSmellSeverity.INFO,
                "excludes": [
                    r"^_",  # Private variables
                ],
            },
            "constant": {
                "pattern": self.PATTERN_SCREAMING_SNAKE_CASE,
                "description": "SCREAMING_SNAKE_CASE",
                "smell_type": CodeSmellType.SCREAMING_SNAKE_CASE_VIOLATION_CONSTANT,
                "severity": CodeSmellSeverity.MINOR,
                "excludes": [r"^_"],
            },
        }
