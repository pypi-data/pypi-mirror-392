from typing import Dict

from metripy.LangAnalyzer.Generic.CodeSmell.CodeSmell import (
    CodeSmellSeverity,
    CodeSmellType,
)
from metripy.LangAnalyzer.Generic.CodeSmell.Detectors.NamingConventionDetector import (
    NamingConventionDetector,
)


class PhpNamingConventionDetector(NamingConventionDetector):
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
                "pattern": self.PATTERN_CAMEL_CASE,
                "description": "camelCase",
                "smell_type": CodeSmellType.CAMEL_CASE_VIOLATION_FUNCTION,
                "severity": CodeSmellSeverity.MINOR,
                "excludes": [
                    r"^__construct$",
                    r"^__destruct$",
                    r"^__invoke$",
                ],
            },
            "variable": {
                "pattern": self.PATTERN_CAMEL_CASE,
                "description": "camelCase",
                "smell_type": CodeSmellType.CAMEL_CASE_VIOLATION_VARIABLE,
                "severity": CodeSmellSeverity.INFO,
                "excludes": [],
            },
            "constant": {
                "pattern": self.PATTERN_SCREAMING_SNAKE_CASE,
                "description": "SCREAMING_SNAKE_CASE",
                "smell_type": CodeSmellType.SCREAMING_SNAKE_CASE_VIOLATION_CONSTANT,
                "severity": CodeSmellSeverity.MINOR,
                "excludes": [],
            },
        }
