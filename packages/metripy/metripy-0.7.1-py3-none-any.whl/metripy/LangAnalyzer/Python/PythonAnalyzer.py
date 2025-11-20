from pathlib import Path

from radon.complexity import cc_visit
from radon.metrics import Halstead, HalsteadReport, h_visit, mi_visit
from radon.visitors import Class, Function

from metripy.Application.Config.ProjectConfig import ProjectConfig
from metripy.LangAnalyzer.AbstractLangAnalyzer import AbstractLangAnalyzer
from metripy.LangAnalyzer.Python.PythonImportsAnalyzer import PythonImportsAnalyzer
from metripy.Tree.ClassNode import ClassNode
from metripy.Tree.FunctionNode import FunctionNode
from metripy.LangAnalyzer.Python.Ast.PythonAstParser import PythonAstParser
from metripy.LangAnalyzer.Python.Metrics.PythonCognitiveComplexityCalculator import (
    PythonCognitiveComplexityCalculator,
)

class PythonAnalyzer(AbstractLangAnalyzer):

    def __init__(self, project_config: ProjectConfig):
        super().__init__(project_config)

    def get_lang_name(self) -> str:
        return "Python"

    def get_supported_extensions(self) -> tuple[str]:
        return (".py",)

    @staticmethod
    def extract_project_root(filename: str) -> str:
        """Extract the project root package name from a file path.

        For example:
            ./metripy/Tree/ModuleNode.py -> "metripy"
            /path/to/metripy/LangAnalyzer/Python/PythonAnalyzer.py -> "metripy"

        Args:
            filename: The file path

        Returns:
            The project root package name
        """
        path = Path(filename)
        parts = path.parts

        # Find the first part that looks like a Python package
        # Skip common prefixes like '.', '..', absolute path components
        for part in parts:
            # Skip current/parent directory markers and common non-package directories
            if part in (".", "..", "/"):
                continue
            # Check if it's likely a Python package (contains letters and possibly underscores)
            if part and not part.startswith(".") and any(c.isalpha() for c in part):
                return part

        # Fallback: just return the first non-special directory
        return parts[0] if parts else "metripy"

    def analyze(self, code: str, filename: str) -> None:
        classes: dict[str, ClassNode] = {}
        functions: dict[str, FunctionNode] = {}
        cc = cc_visit(code)
        for item in cc:
            if isinstance(item, Class):
                full_name = self.full_name(filename, item.name)
                classes[full_name] = ClassNode(
                    full_name,
                    item.name,
                    item.lineno,
                    item.col_offset,
                    item.real_complexity,
                )
            elif isinstance(item, Function):
                full_class_name = self.full_name(filename, item.classname)
                full_name = self.full_name(filename, item.name)
                function_node = FunctionNode(
                    full_name, item.name, item.lineno, item.col_offset, item.complexity
                )
                function_node.line_end = item.endline
                if item.is_method:
                    class_node = classes.get(full_class_name)
                    if class_node is not None:
                        class_node.functions.append(function_node)
                    else:
                        raise ValueError(
                            f"Class node not found for function {full_class_name}"
                        )
                functions[full_name] = function_node
            else:
                raise ValueError(f"Unknown item type: {type(item)}")

        module_node = self.create_module_node(filename, code)
        module_node.classes.extend(classes.values())
        module_node.functions.extend(functions.values())

        h = h_visit(code)
        assert isinstance(h, Halstead)
        function_name: str
        report: HalsteadReport
        for function_name, report in h.functions:
            full_name = self.full_name(filename, function_name)
            function_node = functions.get(full_name)
            if function_node is not None:
                function_node.h1 = report.h1
                function_node.h2 = report.h2
                function_node.N1 = report.N1
                function_node.N2 = report.N2
                function_node.vocabulary = report.vocabulary
                function_node.length = report.length
                function_node.calculated_length = report.calculated_length
                function_node.volume = report.volume
                function_node.difficulty = report.difficulty
                function_node.effort = report.effort
                function_node.bugs = report.bugs
                function_node.time = report.time
                function_node.calc_mi()
            else:
                raise ValueError(f"Function node not found for function {full_name}")

        code_lines = code.split("\n")
        for func_name, function_node in functions.items():
            if function_node.maintainability_index != 0:
                continue
            # if MI is 0, we want to take another look, radon does not like boring functions

            lines = code_lines[function_node.lineno : function_node.line_end]
            self.add_function_halstead_metrics(function_node, "\n".join(lines))

        maintainability_index = mi_visit(code, True)
        module_node.maintainability_index = maintainability_index

        # Extract same-project imports and the import name of this module
        project_root = [
            p for p in Path(filename).parts if p.isalpha() and not p.startswith(".")
        ][0]
        module_node.import_name = PythonImportsAnalyzer.extract_import_name(
            filename, project_root
        )
        module_node.imports = PythonImportsAnalyzer.extract_imports(code, project_root)

        self.modules[module_node.full_name] = module_node

        self.duplicate_detector.add_code(filename, code)

        module_node.code_smells = self.code_smell_detector.detect_all(filename, code)

        parser = PythonAstParser()
        parser.parse(code)
        cognitive_complexities = PythonCognitiveComplexityCalculator(
            parser
        ).calculate_for_all_functions()
        for func_name, complexity in cognitive_complexities.items():
            full_name = self.full_name(filename, func_name)
            function_node = functions.get(full_name)
            if function_node is not None:
                function_node.cognitive_complexity = complexity
            else:
                raise ValueError(f"Function node not found for function {full_name}")

    def get_duplicates(self) -> list[dict]:
        return self.duplicate_detector.get_duplicates()
