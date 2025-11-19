from term_piechart import Pie

from metripy.Dependency.Dependency import Dependency
from metripy.Report.Cli.AbstractFormatter import AbstractFormatter


class DependencyMetricsFormatter(AbstractFormatter):
    def format(self, dependencies: list[Dependency]):
        return f"""
========= Dependency Metrics =========
{self._format_dependencies(dependencies)}

{self._format_license_distribution(dependencies)}
"""

    def _format_dependencies(self, dependencies: list[Dependency]) -> str:
        return self.format_table(
            [
                "Name",
                "Current Version",
                "Latest Version",
                "Status",
                "Type",
                "Description",
                "Repository",
                "Licenses",
            ],
            [
                [
                    dependency.name,
                    dependency.version,
                    dependency.latest,
                    dependency.status,
                    dependency.type,
                    self._shorten_description(dependency.description),
                    dependency.repository,
                    ",".join(dependency.license),
                ]
                for dependency in dependencies
            ],
        )

    def _shorten_description(self, description: str) -> str:
        if len(description) > 30:
            return description[:30] + "..."
        return description

    def _format_license_distribution(self, dependencies: list[Dependency]) -> str:
        license_distribution = Dependency.get_lisence_distribution(dependencies)
        data = [
            {"name": license, "value": count}
            for license, count in license_distribution.items()
        ]
        pie = Pie(data, radius=5, autocolor=True, autocolor_pastel_factor=0.1)
        return pie.render()
