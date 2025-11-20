from metripy.Application.Config.CodeSmellConfig import CodeSmellConfig
from metripy.LangAnalyzer.Generic.CodeSmell.CodeSmell import CodeSmell
from metripy.LangAnalyzer.Generic.CodeSmell.GenericCodeSmellDetector import GenericCodeSmellDetector
from typing import List

class TypescriptCodeSmellDetector:
    def __init__(self, config: CodeSmellConfig):
        self.config = config

    def detect_all(self, filename: str, code: str) -> List[CodeSmell]:
        detector = GenericCodeSmellDetector.for_typescript(self.config, filename, code)
        return detector.detect_all()