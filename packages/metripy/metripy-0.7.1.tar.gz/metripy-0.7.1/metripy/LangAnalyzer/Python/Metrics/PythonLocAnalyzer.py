from metripy.LangAnalyzer.Generic.Metrics.GenericLocAnalyzer import GenericLocAnalyzer

class PythonLocAnalyzer(GenericLocAnalyzer):
    def is_single_comment(self, line: str) -> bool:
        return line.startswith("#")

    def is_multiline_comment_start(self, line: str) -> bool:
        return line.startswith('"""') or line.startswith("'''")

    def is_multiline_comment_end(self, line: str, started_on_same_line: bool=False) -> bool:
        if started_on_same_line:
            return (line.endswith('"""') or line.endswith("'''")) and len(line) > 3
        return line.endswith('"""') or line.endswith("'''")

    def count_logical_lines(self, line: str) -> int:
        # Rough heuristic: split by ';'
        return len([stmt for stmt in line.split(";") if stmt.strip()])
