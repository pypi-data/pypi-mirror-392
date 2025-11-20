from metripy.LangAnalyzer.Generic.Metrics.GenericLocAnalyzer import GenericLocAnalyzer

class PhpLocAnalyzer(GenericLocAnalyzer):
    def is_single_comment(self, line: str) -> bool:
        # PHP single-line comments start with // or #
        return line.startswith("//") or line.startswith("#")

    def is_multiline_comment_start(self, line: str) -> bool:
        # Multi-line comments start with /* in PHP
        return line.startswith("/*")

    def is_multiline_comment_end(self, line: str, started_on_same_line: bool=False) -> bool:
        # Multi-line comments end with */ in PHP
        if started_on_same_line:
            return line.endswith("*/") and len(line) > 4
        return line.endswith("*/")

    def count_logical_lines(self, line: str) -> int:
        # Rough heuristic: split by ';' for statements
        return len([stmt for stmt in line.split(";") if stmt.strip()])
