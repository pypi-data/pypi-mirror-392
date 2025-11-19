from metripy.Metric.Code.FileMetrics import FileMetrics
from metripy.Metric.Code.Segmentor import Segmentor
from metripy.Report.Cli.AbstractFormatter import AbstractFormatter
from metripy.Tree.FunctionNode import FunctionNode


class TopOffendersFormatter(AbstractFormatter):
    def format(self, file_metrics: list[FileMetrics]):
        all_functions: list[FunctionNode] = []
        for fm in file_metrics:
            all_functions.extend(fm.function_nodes)

        return f"""
========= Top Offenders =========
{self._format_loc_offenders(file_metrics, all_functions)}
{self._format_cc_offenders(file_metrics, all_functions)}
{self._format_cog_complexity_offenders(file_metrics, all_functions)}
{self._format_mi_offenders(file_metrics, all_functions)}
"""

    def _format_side_by_side_metrics(self, linfo: list[str], rinfo: list[str]) -> str:
        linfo_width = max(len(l_data) for l_data in linfo)

        table = ""
        for l_data, r_data in zip(linfo, rinfo):
            table += f"{l_data.ljust(linfo_width)} | {r_data}\n"
        return table

    def _format_loc_offenders(
        self, file_metrics: list[FileMetrics], all_functions: list[FunctionNode]
    ) -> str:
        files_ordered = sorted(file_metrics, key=lambda x: x.loc, reverse=True)[:5]
        linfo = ["File Lines of Code"]
        for f in files_ordered:
            segment = Segmentor.get_loc_segment(f.loc)
            color = self.COLORS[segment]
            linfo.append(f"\033[{color}m█\033[0m {f.full_name} ({f.loc})")

        functions_ordered_by_loc = sorted(
            all_functions, key=lambda x: x.get_loc(), reverse=True
        )[:5]
        rinfo = ["Function Size"]
        for f in functions_ordered_by_loc:
            segment = Segmentor.get_method_size_segment(f.get_loc())
            color = self.COLORS[segment]
            rinfo.append(f"\033[{color}m█\033[0m {f.full_name} ({f.get_loc()})")
        return self._format_side_by_side_metrics(linfo, rinfo)

    def _format_cc_offenders(
        self, file_metrics: list[FileMetrics], all_functions: list[FunctionNode]
    ) -> str:
        files_ordered = sorted(file_metrics, key=lambda x: x.totalCc, reverse=True)[:5]
        linfo = ["File Cyclomatic Complexity"]
        for f in files_ordered:
            segment = Segmentor.get_complexity_segment(f.totalCc)
            color = self.COLORS[segment]
            linfo.append(f"\033[{color}m█\033[0m {f.full_name} ({f.totalCc})")

        functions_ordered_by_cc = sorted(
            all_functions, key=lambda x: x.complexity, reverse=True
        )[:5]
        rinfo = ["Function Complexity"]
        for f in functions_ordered_by_cc:
            segment = Segmentor.get_complexity_segment(f.complexity)
            color = self.COLORS[segment]
            rinfo.append(f"\033[{color}m█\033[0m {f.full_name} ({f.complexity})")
        return self._format_side_by_side_metrics(linfo, rinfo)

    def _format_cog_complexity_offenders(
        self, file_metrics: list[FileMetrics], all_functions: list[FunctionNode]
    ) -> str:
        files_ordered = sorted(
            file_metrics, key=lambda x: x.total_cog_complexity, reverse=True
        )[:5]
        linfo = ["File Cognitive Complexity"]
        for f in files_ordered:
            segment = Segmentor.get_complexity_segment(f.total_cog_complexity)
            color = self.COLORS[segment]
            linfo.append(
                f"\033[{color}m█\033[0m {f.full_name} ({f.total_cog_complexity})"
            )

        functions_ordered_by_cog_complexity = sorted(
            all_functions, key=lambda x: x.cognitive_complexity, reverse=True
        )[:5]
        rinfo = ["Function Cognitive Complexity"]
        for f in functions_ordered_by_cog_complexity:
            segment = Segmentor.get_complexity_segment(f.cognitive_complexity)
            color = self.COLORS[segment]
            rinfo.append(
                f"\033[{color}m█\033[0m {f.full_name} ({f.cognitive_complexity})"
            )
        return self._format_side_by_side_metrics(linfo, rinfo)

    def _format_mi_offenders(
        self, file_metrics: list[FileMetrics], all_functions: list[FunctionNode]
    ) -> str:
        files_ordered = sorted(
            file_metrics, key=lambda x: x.maintainabilityIndex, reverse=False
        )[:5]
        linfo = ["File Maintainability Index"]
        for f in files_ordered:
            segment = Segmentor.get_maintainability_segment(f.maintainabilityIndex)
            color = self.COLORS[segment]
            linfo.append(
                f"\033[{color}m█\033[0m {f.full_name} ({round(f.maintainabilityIndex, 2)})"
            )

        functions_ordered_by_mi = sorted(
            all_functions, key=lambda x: x.maintainability_index, reverse=False
        )[:5]
        rinfo = ["Function Maintainability Index"]
        for f in functions_ordered_by_mi:
            segment = Segmentor.get_maintainability_segment(f.maintainability_index)
            color = self.COLORS[segment]
            rinfo.append(
                f"\033[{color}m█\033[0m {f.full_name} ({round(f.maintainability_index, 2)})"
            )
        return self._format_side_by_side_metrics(linfo, rinfo)
