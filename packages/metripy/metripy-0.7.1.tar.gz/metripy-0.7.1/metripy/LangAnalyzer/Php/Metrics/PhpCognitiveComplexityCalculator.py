from metripy.LangAnalyzer.Generic.Metrics.GenericCognitiveComplexityAnalyzer import (
    GenericCognitiveComplexityCalculator,
)


class PhpCognitiveComplexityCalculator(GenericCognitiveComplexityCalculator):
    def get_node_map(self) -> dict[str, str]:
        return {
            "if": "if_statement",
            "else": "else_clause",
            "for": "for_statement",
            "while": "while_statement",
            "try": "try_statement",
            "catch": "catch_clause",
            "switch": "switch_statement",
            "case": "case_statement",
        }
