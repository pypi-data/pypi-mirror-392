from metripy.LangAnalyzer.Python.Metrics.PythonLocAnalyzer import PythonLocAnalyzer
from metripy.LangAnalyzer.Php.Metrics.PhpLocAnalyzer import PhpLocAnalyzer
from metripy.LangAnalyzer.Generic.Metrics.GenericLocAnalyzer import GenericLocAnalyzer
class LocAnalyzerFactory:
    _ANALYZERS = {
        "Python": PythonLocAnalyzer(),
        "PHP": PhpLocAnalyzer(),
        "Typescript": None,
    }

    @staticmethod
    def get_loc_analyzer(language: str) -> GenericLocAnalyzer:
        try:
            return LocAnalyzerFactory._ANALYZERS[language]
        except KeyError:
            raise ValueError(f"No loc analyzer found for language: {language}")
