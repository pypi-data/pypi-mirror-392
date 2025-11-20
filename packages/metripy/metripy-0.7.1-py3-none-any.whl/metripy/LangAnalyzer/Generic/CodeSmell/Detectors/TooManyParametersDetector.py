"""Generic detector for functions with too many parameters"""

from typing import List

from metripy.Application.Config.CodeSmellConfig import CodeSmellConfig
from metripy.LangAnalyzer.Generic.CodeSmell.CodeSmell import (
    CodeSmell,
    CodeSmellSeverity,
    CodeSmellType,
)
from metripy.LangAnalyzer.Generic.CodeSmell.Detectors.BaseDetector import (
    BaseCodeSmellDetector,
)


class TooManyParametersDetector(BaseCodeSmellDetector):
    """Detects functions with too many parameters in any language"""

    def __init__(
        self, filename: str, parser, config: CodeSmellConfig, max_params: int = 5
    ):
        super().__init__(filename, parser, config)
        self.max_params = max_params
        # Language-specific parameters to exclude
        self.excluded_params = {"self", "cls", "this"}

    def detect(self) -> List[CodeSmell]:
        """Detect functions with too many parameters"""
        function_nodes = self.parser.get_function_nodes()
        if not function_nodes:
            return []

        for func_node in function_nodes:
            func_name = self.parser.extract_function_name(func_node)
            if not func_name:
                continue

            params = self.parser.get_function_parameters(func_node)
            # Filter out language-specific parameters like 'self', 'this'
            filtered_params = [p for p in params if p not in self.excluded_params]
            param_count = len(filtered_params)

            if param_count > self.max_params:

                self.smells.append(
                    CodeSmell(
                        smell_type=CodeSmellType.TOO_MANY_PARAMETERS,
                        severity=CodeSmellSeverity.MAJOR,
                        filename=self.filename,
                        line_number=self.get_line_number(func_node),
                        column=self.get_column(func_node),
                        code_line=self.parser.get_code_line(func_node),
                        message=f"Function '{func_name}' has {param_count} parameters (max recommended: {self.max_params})",
                        symbol=func_name,
                    )
                )

        return self.smells
