from metripy.Metric.Git.GitCodeHotspot import GitCodeHotspot
from metripy.Metric.Git.GitContributor import GitContributor
from metripy.Metric.Git.GitKnowledgeSilo import GitKnowledgeSilo
from metripy.Metric.Git.GitMetrics import GitMetrics
from metripy.Report.Cli.AbstractFormatter import AbstractFormatter


class GitMetricsFormatter(AbstractFormatter):
    def format(self, metrics: GitMetrics):
        return f"""
========= Git Metrics =========
Analysis From: {metrics.analysis_start_date}
Total Commits: {metrics.total_commits}
Average Commit Size: {round(metrics.get_avg_commit_size(), 2)}

Top 5 Silos:
{self._format_silos(metrics.silos)}

Top 5 Hotspots:
{self._format_hotspots(metrics.hotspots)}

Top 5 Contributors:
{self._format_contributors(metrics.contributors)}
"""

    def _format_silos(self, silos: list[GitKnowledgeSilo]) -> str:
        return self.format_table(
            ["File Path", "Owner", "Commits Count", "Risk Level"],
            [
                [silo.file_path, silo.owner, silo.commits_count, silo.risk_level]
                for silo in silos[:5]
            ],
        )

    def _format_hotspots(self, hotspots: list[GitCodeHotspot]) -> str:
        return self.format_table(
            ["File Path", "Changes Count", "Contributors Count", "Risk Level"],
            [
                [
                    hotspot.file_path,
                    hotspot.changes_count,
                    hotspot.contributors_count,
                    hotspot.risk_level,
                ]
                for hotspot in hotspots[:5]
            ],
        )

    def _format_contributors(self, contributors: list[GitContributor]) -> str:
        return self.format_table(
            [
                "Name",
                "Commits Count",
                "Lines Added",
                "Lines Removed",
                "Contribution Percentage",
            ],
            [
                [
                    contributor.name,
                    contributor.commits_count,
                    contributor.lines_added,
                    contributor.lines_removed,
                    contributor.contribution_percentage,
                ]
                for contributor in contributors[:5]
            ],
        )
