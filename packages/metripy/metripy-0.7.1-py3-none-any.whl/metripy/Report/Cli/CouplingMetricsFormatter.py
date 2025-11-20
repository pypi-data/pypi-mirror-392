from metripy.Metric.Code.FileMetrics import FileMetrics
from metripy.Report.Cli.AbstractFormatter import AbstractFormatter


class CouplingMetricsFormatter(AbstractFormatter):
    def format(self, file_metrics: list[FileMetrics]):
        return f"""
========= Coupling Metrics =========
Total Modules: {self._get_total_modules(file_metrics)}
Total Dependencies: {self._get_total_dependencies(file_metrics)}
Max Coupling: {self._get_max_coupling(file_metrics)}
Average Instability: {round(self._get_average_instability(file_metrics), 2)}
{self._format_instability_bar(file_metrics)}
"""

    def _get_total_modules(self, file_metrics: list[FileMetrics]) -> int:
        return len(file_metrics)

    def _get_total_dependencies(self, file_metrics: list[FileMetrics]) -> int:
        return sum(len(f.imports) for f in file_metrics)

    def _get_average_instability(self, file_metrics: list[FileMetrics]) -> float:
        return sum(f.instability for f in file_metrics) / len(file_metrics)

    def _get_max_coupling(self, file_metrics: list[FileMetrics]) -> int:
        return max(f.afferent_coupling + f.efferent_coupling for f in file_metrics)

    def _format_instability_bar(self, file_metrics: list[FileMetrics]) -> str:
        stable = len([f.instability for f in file_metrics if f.instability <= 0.3])
        moderate = len(
            [
                f.instability
                for f in file_metrics
                if f.instability > 0.3 and f.instability <= 0.7
            ]
        )
        unstable = len([f.instability for f in file_metrics if f.instability > 0.7])

        colors = [self.COLORS["good"], self.COLORS["ok"], self.COLORS["critical"]]
        return f"""
{self.colored_stacked_bar([stable, moderate, unstable], colors, width=100)}
{self.colored_stacked_info([stable, moderate, unstable], ["Stable", "Neutral", "Unstable"], colors, width=100)}
"""
