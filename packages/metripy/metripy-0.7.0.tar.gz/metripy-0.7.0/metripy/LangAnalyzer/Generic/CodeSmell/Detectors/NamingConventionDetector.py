"""Generic base for naming convention detection"""

import re
from abc import abstractmethod
from typing import Dict, List

from metripy.Application.Config.CodeSmellConfig import CodeSmellConfig
from metripy.LangAnalyzer.Generic.CodeSmell.CodeSmell import CodeSmell
from metripy.LangAnalyzer.Generic.CodeSmell.Detectors.BaseDetector import (
    BaseCodeSmellDetector,
)


class NamingConventionDetector(BaseCodeSmellDetector):
    """Base class for naming convention detection with language-specific rules"""

    PATTERN_SNAKE_CASE = r"^[a-z][a-z0-9_]*$"
    PATTERN_CAMEL_CASE = r"^[a-z][a-zA-Z0-9]*$"
    PATTERN_PASCAL_CASE = r"^[A-Z][a-zA-Z0-9]*$"
    PATTERN_SCREAMING_SNAKE_CASE = r"^[A-Z][A-Z0-9_]*$"

    def __init__(self, filename: str, parser, config: CodeSmellConfig):
        super().__init__(filename, parser, config)
        # Define naming rules for different elements
        # Override these in language-specific implementations
        self.naming_rules: Dict[str, Dict] = {
            k: v
            for k, v in self._get_naming_rules().items()
            if self.config.is_enabled(v["smell_type"].value)
        }

    @abstractmethod
    def _get_naming_rules(self) -> Dict[str, Dict]:
        """
        Define naming rules for the language.

        Returns dict with structure:
        {
            'class': {
                'pattern': r'^[A-Z][a-zA-Z0-9]*$',  # regex pattern
                'description': 'PascalCase',
                'smell_type': CodeSmellType.PASCAL_CASE_VIOLATION_CLASS,
                'severity': CodeSmellSeverity.MINOR,
                'excludes': []  # patterns to exclude (e.g., magic methods)
            },
            ...
        }
        """
        pass

    def detect(self) -> List[CodeSmell]:
        """Detect naming convention violations"""
        # Check class names
        if "class" in self.naming_rules:
            self._check_classes()

        # Check function names
        if "function" in self.naming_rules:
            self._check_functions()

        # Check variable names
        if "variable" in self.naming_rules:
            self._check_variables()

        return self.smells

    def _check_classes(self) -> None:
        """Check class naming conventions"""
        rule = self.naming_rules["class"]
        class_nodes = self.parser.get_class_nodes()

        for class_node in class_nodes:
            class_name = self.parser.extract_class_name(class_node)
            if not class_name:
                continue

            # Check exclusions
            if self._should_exclude(class_name, rule.get("excludes", [])):
                continue

            if not re.match(rule["pattern"], class_name):
                self.smells.append(
                    CodeSmell(
                        smell_type=rule["smell_type"],
                        severity=rule["severity"],
                        filename=self.filename,
                        line_number=self.get_line_number(class_node),
                        column=self.get_column(class_node),
                        message=f"Class name '{class_name}' should use {rule['description']}",
                        code_line=self.parser.get_code_line(class_node),
                        symbol=class_name,
                    )
                )

    def _check_functions(self) -> None:
        """Check function naming conventions"""
        rule = self.naming_rules["function"]
        function_nodes = self.parser.get_function_nodes()

        for func_node in function_nodes:
            func_name = self.parser.extract_function_name(func_node)
            if not func_name:
                continue

            # Check exclusions
            if self._should_exclude(func_name, rule.get("excludes", [])):
                continue

            if not re.match(rule["pattern"], func_name):
                self.smells.append(
                    CodeSmell(
                        smell_type=rule["smell_type"],
                        severity=rule["severity"],
                        filename=self.filename,
                        line_number=self.get_line_number(func_node),
                        column=self.get_column(func_node),
                        message=f"Function name '{func_name}' should use {rule['description']}",
                        code_line=self.parser.get_code_line(func_node),
                        symbol=func_name,
                    )
                )

    def _check_variables(self) -> None:
        """Check variable naming conventions"""
        rule = self.naming_rules["variable"]
        var_nodes = self.parser.get_variable_assignment_nodes()

        for var_node in var_nodes:
            var_name = self.parser.extract_variable_name(var_node)
            if not var_name:
                continue

            # Handle multiple variables in one statement
            var_names = [v.strip() for v in var_name.split(",")]

            for name in var_names:
                # Check exclusions
                if self._should_exclude(name, rule.get("excludes", [])):
                    continue

                # Check for constants (all uppercase)
                if "constant" in self.naming_rules and name.isupper():
                    const_rule = self.naming_rules["constant"]
                    if not re.match(const_rule["pattern"], name):
                        self.smells.append(
                            CodeSmell(
                                smell_type=const_rule["smell_type"],
                                severity=const_rule["severity"],
                                filename=self.filename,
                                line_number=self.get_line_number(var_node),
                                column=self.get_column(var_node),
                                message=f"Constant '{name}' should use {const_rule['description']}",
                                code_line=self.parser.get_code_line(var_node),
                                symbol=name,
                            )
                        )
                elif not re.match(rule["pattern"], name):
                    self.smells.append(
                        CodeSmell(
                            smell_type=rule["smell_type"],
                            severity=rule["severity"],
                            filename=self.filename,
                            line_number=self.get_line_number(var_node),
                            column=self.get_column(var_node),
                            message=f"Variable name '{name}' should use {rule['description']}",
                            code_line=self.parser.get_code_line(var_node),
                            symbol=name,
                        )
                    )

    def _should_exclude(self, name: str, exclusions: List[str]) -> bool:
        """Check if name should be excluded from checking"""
        for exclusion in exclusions:
            if callable(exclusion):
                if exclusion(name):
                    return True
            elif re.match(exclusion, name):
                return True
        return False
