from metripy.LangAnalyzer.Python.CodeSmell.PythonCodeSmellDetector import PythonCodeSmellDetector
from metripy.LangAnalyzer.Php.CodeSmell.PhpCodeSmellDetector import PhpCodeSmellDetector
from metripy.LangAnalyzer.Generic.CodeSmell.GenericCodeSmellDetector import GenericCodeSmellDetector
from metripy.Application.Config.CodeSmellConfig import CodeSmellConfig
from metripy.LangAnalyzer.Typescript.CodeSmell.TypescriptCodeSmellDetector import TypescriptCodeSmellDetector

class CodeSmellDetectorFactory:
    _DETECTORS = {
        "Python": PythonCodeSmellDetector,
        "PHP": PhpCodeSmellDetector,
        "Typescript": TypescriptCodeSmellDetector,
    }

    @staticmethod
    def get_code_smell_detector(language: str, config: CodeSmellConfig) -> GenericCodeSmellDetector:
        try:
            return CodeSmellDetectorFactory._DETECTORS[language](config)
        except KeyError:
            raise ValueError(f"No code smell detector found for language: {language}")
