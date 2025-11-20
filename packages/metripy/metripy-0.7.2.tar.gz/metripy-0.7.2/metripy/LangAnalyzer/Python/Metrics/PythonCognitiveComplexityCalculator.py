from metripy.LangAnalyzer.Generic.Metrics.GenericCognitiveComplexityAnalyzer import (
    GenericCognitiveComplexityCalculator,
)


class PythonCognitiveComplexityCalculator(GenericCognitiveComplexityCalculator):
    def get_node_map(self) -> dict[str, str]:
        return {
            "if": "if_statement",
            "else": "else_clause",
            "for": "for_statement",
            "while": "while_statement",
            "try": "try_statement",
            "except": "except_clause",
            "switch": None,
            "case": None,
        }
