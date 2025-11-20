import json

from metripy.Metric.ProjectMetrics import ProjectMetrics
from metripy.Report.Html.PageRenderer import PageRenderer


class CodeSmellsPageRenderer(PageRenderer):
    def __init__(self, template_dir: str, output_dir: str, project_name: str):
        super().__init__(template_dir, output_dir, project_name)

    def render(self, metrics: ProjectMetrics):
        data = {
            x.full_name: [y.to_dict() for y in x.code_smells]
            for x in metrics.file_metrics
            if len(x.code_smells) > 0
        }

        self.render_template(
            "code_smells.html",
            {
                "file_code_smells": json.dumps(data),
            },
        )
