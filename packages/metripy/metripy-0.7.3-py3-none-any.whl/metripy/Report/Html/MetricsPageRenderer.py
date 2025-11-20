from metripy.Metric.ProjectMetrics import ProjectMetrics
from metripy.Report.Html.PageRenderer import PageRenderer


class MetricsPageRenderer(PageRenderer):
    def __init__(self, template_dir: str, output_dir: str, project_name: str):
        super().__init__(template_dir, output_dir, project_name)

    def render(self, metrics: ProjectMetrics):
        # only showing static info
        self.render_template("metrics.html", {})
