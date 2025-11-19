"""Code smell data structures - moved from Generic/CodeSmell.py"""

from enum import Enum
from typing import Optional


class CodeSmellType(Enum):
    """Types of code smells that can be detected"""

    # Dead Code
    UNUSED_VARIABLE = "unused_variable"
    UNUSED_IMPORT = "unused_import"
    UNUSED_FUNCTION = "unused_function"
    UNUSED_CLASS = "unused_class"
    UNUSED_PARAMETER = "unused_parameter"

    # Naming Conventions function
    SNAKE_CASE_VIOLATION_FUNCTION = "snake_case_violation_function"
    CAMEL_CASE_VIOLATION_FUNCTION = "camel_case_violation_function"
    PASCAL_CASE_VIOLATION_FUNCTION = "pascal_case_violation_function"
    # Naming Conventions variable
    SNAKE_CASE_VIOLATION_VARIABLE = "snake_case_violation_variable"
    CAMEL_CASE_VIOLATION_VARIABLE = "camel_case_violation_variable"
    PASCAL_CASE_VIOLATION_VARIABLE = "pascal_case_violation_variable"
    # Naming Conventions class
    SNAKE_CASE_VIOLATION_CLASS = "snake_case_violation_class"
    PASCAL_CASE_VIOLATION_CLASS = "pascal_case_violation_class"
    CAMEL_CASE_VIOLATION_CLASS = "camel_case_violation_class"
    # Naming Conventions constant
    SCREAMING_SNAKE_CASE_VIOLATION_CONSTANT = "screaming_snake_case_violation_constant"

    # Code Smells
    TOO_MANY_PARAMETERS = "too_many_parameters"
    LONG_FUNCTION = "long_function"


class CodeSmellSeverity(Enum):
    """Severity levels for code smells"""

    INFO = "info"
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


class CodeSmell:
    """Represents a detected code smell in the codebase"""

    def __init__(
        self,
        smell_type: CodeSmellType,
        severity: CodeSmellSeverity,
        filename: str,
        line_number: int,
        column: int,
        message: str,
        code_line: str,
        symbol: Optional[str] = None,
        end_line: Optional[int] = None,
    ):
        self.smell_type = smell_type
        self.severity = severity
        self.filename = filename
        self.line_number = line_number
        self.column = column
        self.code_line = code_line
        self.message = message
        self.symbol = symbol  # The name of the variable/function/class involved
        self.end_line = end_line or line_number

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            "type": self.smell_type.value,
            "severity": self.severity.value,
            "filename": self.filename,
            "line": self.line_number,
            "column": self.column,
            "end_line": self.end_line,
            "message": self.message,
            "symbol": self.symbol,
            "code_line": self.code_line,
        }

    def __repr__(self) -> str:
        return (
            f"CodeSmell({self.severity.value}: {self.smell_type.value} "
            f"at {self.filename}:{self.line_number} - {self.message})"
        )
