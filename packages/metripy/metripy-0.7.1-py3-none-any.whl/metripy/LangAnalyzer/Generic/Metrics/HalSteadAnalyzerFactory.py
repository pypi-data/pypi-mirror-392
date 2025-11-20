from metripy.LangAnalyzer.Python.Metrics.PythonHalSteadAnalyzer import PythonHalSteadAnalyzer
from metripy.LangAnalyzer.Php.Metrics.PhpHalSteadAnalyzer import PhpHalSteadAnalyzer
from metripy.LangAnalyzer.Generic.Metrics.GenericHalSteadAnalyzer import GenericHalSteadAnalyzer
from metripy.LangAnalyzer.Typescript.TypescriptHalSteadAnalyzer import TypeScriptHalSteadAnalyzer

class HalSteadAnalyzerFactory:
    _ANALYZERS = {
        "Python": PythonHalSteadAnalyzer(),
        "PHP": PhpHalSteadAnalyzer(),
        "Typescript": TypeScriptHalSteadAnalyzer(),
    }

    @staticmethod
    def get_halstead_analyzer(language: str) -> GenericHalSteadAnalyzer:
        try:
            return HalSteadAnalyzerFactory._ANALYZERS[language]
        except KeyError:
            raise ValueError(f"No halstead analyzer found for language: {language}")