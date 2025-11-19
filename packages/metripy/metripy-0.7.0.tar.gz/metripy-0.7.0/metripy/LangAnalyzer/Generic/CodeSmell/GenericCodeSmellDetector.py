"""Generic code smell detector that works with any language parser"""

from typing import List, Type

from metripy.Application.Config.CodeSmellConfig import CodeSmellConfig
from metripy.LangAnalyzer.Generic.CodeSmell.AstParser import AstParser
from metripy.LangAnalyzer.Generic.CodeSmell.CodeSmell import CodeSmell
from metripy.LangAnalyzer.Generic.CodeSmell.Detectors.BaseDetector import (
    BaseCodeSmellDetector,
)
from metripy.LangAnalyzer.Generic.CodeSmell.Detectors.TooManyParametersDetector import (
    TooManyParametersDetector,
)
from metripy.LangAnalyzer.Generic.CodeSmell.Detectors.UnusedFunctionsDetector import (
    UnusedFunctionsDetector,
)
from metripy.LangAnalyzer.Generic.CodeSmell.Detectors.UnusedImportsDetector import (
    UnusedImportsDetector,
)


class GenericCodeSmellDetector:
    """
    Generic code smell detector that orchestrates multiple detectors.
    Works with any language that has an AstParser implementation.
    """

    def __init__(
        self,
        config: CodeSmellConfig,
        filename: str,
        code: str,
        parser: AstParser,
        naming_detector_class: Type[BaseCodeSmellDetector] | None = None,
        max_params: int = 5,
    ):
        """
        Initialize generic code smell detector.

        Args:
            filename: Path to the file being analyzed
            code: Source code to analyze
            parser: Language-specific AST parser
            naming_detector_class: Optional language-specific naming convention detector
            max_params: Maximum number of parameters for functions
        """
        self.config = config
        self.filename = filename
        self.code = code
        self.parser = parser
        self.naming_detector_class = naming_detector_class
        self.max_params = max_params

        # Parse the code
        self.parser.parse(code)

    def detect_all(self) -> List[CodeSmell]:
        """Run all code smell detection checks"""
        if self.parser.tree is None:
            return []

        all_smells = []

        # Create and run generic detectors
        detectors: dict[str, BaseCodeSmellDetector] = {
            "unused_imports": UnusedImportsDetector(
                self.filename, self.parser, self.config
            ),
            "unused_functions": UnusedFunctionsDetector(
                self.filename, self.parser, self.config
            ),
            "too_many_parameters": TooManyParametersDetector(
                self.filename, self.parser, self.config, self.max_params
            ),
        }

        # Add naming convention detector if provided
        if self.naming_detector_class:
            detectors["naming_convention"] = self.naming_detector_class(
                self.filename, self.parser, self.config
            )

        # Run all configured detectors
        for detector_name, detector in detectors.items():
            if self.config.is_enabled(detector_name):
                all_smells.extend(detector.detect())

        return all_smells

    @staticmethod
    def for_python(
        config: CodeSmellConfig, filename: str, code: str
    ) -> "GenericCodeSmellDetector":
        """Factory method to create detector for Python"""
        from metripy.LangAnalyzer.Python.Ast.PythonAstParser import PythonAstParser
        from metripy.LangAnalyzer.Python.CodeSmell.PythonNamingConventionDetector import (
            PythonNamingConventionDetector,
        )

        parser = PythonAstParser()
        return GenericCodeSmellDetector(
            config,
            filename,
            code,
            parser,
            naming_detector_class=PythonNamingConventionDetector,
        )

    @staticmethod
    def for_php(
        config: CodeSmellConfig, filename: str, code: str
    ) -> "GenericCodeSmellDetector":
        """Factory method to create detector for PHP"""
        from metripy.LangAnalyzer.Php.Ast.PhpAstParser import PhpAstParser
        from metripy.LangAnalyzer.Php.CodeSmell.PhpNamingConventionDetector import (
            PhpNamingConventionDetector,
        )

        parser = PhpAstParser()
        return GenericCodeSmellDetector(
            config,
            filename,
            code,
            parser,
            naming_detector_class=PhpNamingConventionDetector,
        )

    @staticmethod
    def for_typescript(
        config: CodeSmellConfig, filename: str, code: str
    ) -> "GenericCodeSmellDetector":
        """Factory method to create detector for TypeScript"""
        from metripy.LangAnalyzer.Typescript.Ast.TypescriptAstParser import (
            TypescriptAstParser,
        )
        from metripy.LangAnalyzer.Typescript.CodeSmell.TypescriptNamingConventionDetector import (
            TypescriptNamingConventionDetector,
        )

        parser = TypescriptAstParser()
        return GenericCodeSmellDetector(
            config,
            filename,
            code,
            parser,
            naming_detector_class=TypescriptNamingConventionDetector,
        )
