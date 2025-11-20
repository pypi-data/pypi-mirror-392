from metripy.LangAnalyzer.Generic.CodeSmell.CodeSmell import CodeSmellSeverity
from metripy.Metric.Code.FileMetrics import FileMetrics
from metripy.Report.Cli.AbstractFormatter import AbstractFormatter


class CodeSmellsFormatter(AbstractFormatter):
    def format(self, file_metrics: list[FileMetrics]):
        return f"""
========= Code Smells =========
{self._format_code_smells(file_metrics)}
"""

    def _format_code_smells(self, file_metrics: list[FileMetrics]) -> str:
        major = 0
        critical = 0
        minor = 0
        info = 0
        for f in file_metrics:
            for smell in f.code_smells:
                if smell.severity == CodeSmellSeverity.MAJOR:
                    major += 1
                if smell.severity == CodeSmellSeverity.CRITICAL:
                    critical += 1
                if smell.severity == CodeSmellSeverity.MINOR:
                    minor += 1
                if smell.severity == CodeSmellSeverity.INFO:
                    info += 1
        colors = [
            "34",
            self.COLORS["ok"],
            self.COLORS["warning"],
            self.COLORS["critical"],
        ]
        data = [info, minor, major, critical]
        labels = ["Info", "Minor", "Major", "Critical"]

        return f"""Total Code Smells: {sum(data)}

{self.colored_stacked_bar(data, colors, width=100)}
{self.colored_stacked_info(data, labels, colors, width=100)}
"""
