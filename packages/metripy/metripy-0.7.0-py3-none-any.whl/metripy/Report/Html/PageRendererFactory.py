from metripy.Report.Html.CodeSmellsPageRenderer import CodeSmellsPageRenderer
from metripy.Report.Html.CouplingPageRenderer import CouplingPageRenderer
from metripy.Report.Html.DependencyPageRenderer import DependencyPageRenderer
from metripy.Report.Html.FilesPageRenderer import FilesPageRenderer
from metripy.Report.Html.GitAnalysisPageRenderer import GitAnalysisPageRenderer
from metripy.Report.Html.IndexPageRenderer import IndexPageRenderer
from metripy.Report.Html.TopOffendersPageRenderer import TopOffendersPageRenderer
from metripy.Report.Html.TrendsPageRenderer import TrendsPageRenderer


class PageRendererFactory:
    def __init__(self, template_dir: str, output_dir: str, project_name: str):
        self.template_dir = template_dir
        self.output_dir = output_dir
        self.project_name = project_name

    def create_index_page_renderer(self) -> IndexPageRenderer:
        return IndexPageRenderer(self.template_dir, self.output_dir, self.project_name)

    def create_files_page_renderer(self) -> FilesPageRenderer:
        return FilesPageRenderer(self.template_dir, self.output_dir, self.project_name)

    def create_top_offenders_page_renderer(self) -> TopOffendersPageRenderer:
        return TopOffendersPageRenderer(
            self.template_dir, self.output_dir, self.project_name
        )

    def create_git_analysis_page_renderer(self) -> GitAnalysisPageRenderer:
        return GitAnalysisPageRenderer(
            self.template_dir, self.output_dir, self.project_name
        )

    def create_dependency_page_renderer(self) -> DependencyPageRenderer:
        return DependencyPageRenderer(
            self.template_dir, self.output_dir, self.project_name
        )

    def create_trends_page_renderer(self) -> TrendsPageRenderer:
        return TrendsPageRenderer(self.template_dir, self.output_dir, self.project_name)

    def create_coupling_page_renderer(self) -> CouplingPageRenderer:
        return CouplingPageRenderer(
            self.template_dir, self.output_dir, self.project_name
        )

    def create_code_smells_page_renderer(self) -> CodeSmellsPageRenderer:
        return CodeSmellsPageRenderer(
            self.template_dir, self.output_dir, self.project_name
        )
