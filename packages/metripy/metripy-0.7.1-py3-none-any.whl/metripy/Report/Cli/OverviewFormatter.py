from metripy.Metric.Code.AggregatedMetrics import AggregatedMetrics
from metripy.Metric.ProjectMetrics import ProjectMetrics
from metripy.Report.Cli.AbstractFormatter import AbstractFormatter


class OverviewFormatter(AbstractFormatter):

    def format(self, metrics: ProjectMetrics):
        return f"""
========= Overview =========

These metrics are file based and show the average values per file. Outliers might be hidden.

{self._format_loc_metrics(metrics.total_code_metrics)}
{self._format_cyclomatic_complexity_metrics(metrics.total_code_metrics)}
{self._format_cognitive_complexity_metrics(metrics.total_code_metrics)}
{self._format_maintainability_metrics(metrics.total_code_metrics)}
{self._format_method_size_metrics(metrics.total_code_metrics)}
"""

    def _format_loc_metrics(self, metrics: AggregatedMetrics) -> str:

        values = metrics.segmentation_data["loc"].to_dict().values()
        labels = ["small", "medium", "large", "very large"]
        return f"""
Lines of Code:
{metrics.loc} total lines
{self.colored_stacked_bar(values, self.COLORS.values(), width=100)}
{self.colored_stacked_info(values, labels, self.COLORS.values(), width=100)}
"""

    def _format_cyclomatic_complexity_metrics(self, metrics: AggregatedMetrics) -> str:
        values = metrics.segmentation_data["complexity"].to_dict().values()
        labels = ["simple", "moderate", "complex", "very complex"]
        return f"""Avg. Cyclomatic Complexity:
{round(metrics.avgCcPerFunction, 1)} avg per function
{self.colored_stacked_bar(values, self.COLORS.values(), width=100)}
{self.colored_stacked_info(values, labels, self.COLORS.values(), width=100)}
"""

    def _format_cognitive_complexity_metrics(self, metrics: AggregatedMetrics) -> str:
        values = metrics.segmentation_data["cognitiveComplexity"].to_dict().values()
        labels = ["low", "medium", "high", "very high"]
        return f"""Avg. Cognitive Complexity:
{round(metrics.avg_cog_complexity_per_function, 1)} avg per function
{self.colored_stacked_bar(values, self.COLORS.values(), width=100)}
{self.colored_stacked_info(values, labels, self.COLORS.values(), width=100)}
"""

    def _format_maintainability_metrics(self, metrics: AggregatedMetrics) -> str:
        values = metrics.segmentation_data["maintainability"].to_dict().values()
        labels = ["excellent", "good", "fair", "poor"]
        return f"""Maintainability:
{round(metrics.maintainabilityIndex, 1)} / 100 on average
{self.colored_stacked_bar(values, self.COLORS.values(), width=100)}
{self.colored_stacked_info(values, labels, self.COLORS.values(), width=100)}
"""

    def _format_method_size_metrics(self, metrics: AggregatedMetrics) -> str:
        values = metrics.segmentation_data["methodSize"].to_dict().values()
        labels = ["concise", "optimal", "large", "too large"]
        return f"""Method Size:
{round(metrics.avgLocPerFunction, 1)} lines avg per function
{self.colored_stacked_bar(values, self.COLORS.values(), width=100)}
{self.colored_stacked_info(values, labels, self.COLORS.values(), width=100)}
"""
