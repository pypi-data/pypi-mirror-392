from metripy.Application.Config.Config import Config
from metripy.Component.Output.CliOutput import CliOutput
from metripy.Metric.ProjectMetrics import ProjectMetrics
from metripy.Report.Cli.CodeSmellsFormatter import CodeSmellsFormatter
from metripy.Report.Cli.CouplingMetricsFormatter import CouplingMetricsFormatter
from metripy.Report.Cli.DependencyMetricsFormatter import DependencyMetricsFormatter
from metripy.Report.Cli.GitMetricsFormatter import GitMetricsFormatter
from metripy.Report.Cli.OverviewFormatter import OverviewFormatter
from metripy.Report.Cli.TopOffendersFormatter import TopOffendersFormatter
from metripy.Report.ReporterInterface import ReporterInterface


class Reporter(ReporterInterface):
    def __init__(self, config: Config, output: CliOutput):
        self.config = config
        self.output = output

    def generate(self, metrics: ProjectMetrics):
        self.output.writeln(OverviewFormatter().format(metrics))
        self.output.writeln(TopOffendersFormatter().format(metrics.file_metrics))
        self.output.writeln(CouplingMetricsFormatter().format(metrics.file_metrics))
        self.output.writeln(CodeSmellsFormatter().format(metrics.file_metrics))
        self.output.writeln(GitMetricsFormatter().format(metrics.git_metrics))
        self.output.writeln(DependencyMetricsFormatter().format(metrics.dependencies))
