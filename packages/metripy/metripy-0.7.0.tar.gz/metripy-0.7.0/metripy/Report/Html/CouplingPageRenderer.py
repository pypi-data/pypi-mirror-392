import json

from metripy.Metric.ProjectMetrics import ProjectMetrics
from metripy.Report.Html.PageRenderer import PageRenderer


class CouplingPageRenderer(PageRenderer):
    def __init__(self, template_dir: str, output_dir: str, project_name: str):
        super().__init__(template_dir, output_dir, project_name)

    def render(self, metrics: ProjectMetrics):
        # Convert file metrics to list of dictionaries for JSON serialization
        metrics_list = []
        for file_metric in metrics.file_metrics:
            metric_dict = {
                "full_name": file_metric.full_name,
                "import_name": file_metric.import_name,
                "imports": file_metric.imports if file_metric.imports else [],
                "imported_by": (
                    file_metric.imported_by if file_metric.imported_by else []
                ),
                "afferent_coupling": file_metric.afferent_coupling,
                "efferent_coupling": file_metric.efferent_coupling,
                "instability": file_metric.instability,
            }
            metrics_list.append(metric_dict)

        self.render_template(
            "coupling.html",
            {
                "metrics_json": json.dumps(metrics_list, indent=2),
            },
        )
