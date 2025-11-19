from typing import Self

from metripy.LangAnalyzer.Generic.CodeSmell.CodeSmell import CodeSmell
from metripy.Metric.Code.Segmentor import Segmentor
from metripy.Metric.Trend.FileTrendMetric import FileTrendMetric
from metripy.Tree.ClassNode import ClassNode
from metripy.Tree.FunctionNode import FunctionNode


class FileMetrics:
    def __init__(
        self,
        full_name: str,
        loc: int,
        totalCc: int,
        avgCcPerFunction: float,
        maintainabilityIndex: float,
        avgLocPerFunction: float,
        class_nodes: list[ClassNode],
        function_nodes: list[FunctionNode],
        import_name: str | None,
        imports: list[str] | None,
        code_smells: list[CodeSmell],
        total_cog_complexity: int,
        avg_cog_complexity_per_function: float,
    ):
        self.full_name = full_name
        self.loc = loc
        self.totalCc = totalCc
        self.avgCcPerFunction = avgCcPerFunction
        self.maintainabilityIndex = maintainabilityIndex
        self.avgLocPerFunction = avgLocPerFunction
        self.class_nodes = class_nodes
        self.function_nodes = function_nodes
        self.trend: FileTrendMetric | None = None
        self.import_name = import_name
        self.imports: list[str] | None = imports
        self.imported_by: list[str] | None = None
        self.afferent_coupling: int = 0
        self.efferent_coupling: int = 0
        self.instability: float = 0
        self.code_smells: list[CodeSmell] = code_smells
        self.total_cog_complexity = total_cog_complexity
        self.avg_cog_complexity_per_function = avg_cog_complexity_per_function

    def to_dict(self) -> dict:
        return {
            "full_name": self.full_name,
            "loc": self.loc,
            "loc_segment": Segmentor.get_loc_segment(self.loc),
            "totalCc": self.totalCc,
            "complexity_segment": Segmentor.get_complexity_segment(
                self.avgCcPerFunction
            ),
            "avgCcPerFunction": self.avgCcPerFunction,
            "maintainabilityIndex": round(self.maintainabilityIndex, 2),
            "maintainability_segment": Segmentor.get_maintainability_segment(
                self.maintainabilityIndex
            ),
            "avgLocPerFunction": self.avgLocPerFunction,
            "method_size_segment": Segmentor.get_method_size_segment(
                self.avgLocPerFunction
            ),
            "class_nodes": [node.to_dict() for node in self.class_nodes],
            "function_nodes": [node.to_dict() for node in self.function_nodes],
            "import_name": self.import_name,
            "imports": self.imports,
            "afferent_coupling": self.afferent_coupling,
            "efferent_coupling": self.efferent_coupling,
            "instability": round(self.instability, 2),
            "total_cog_complexity": self.total_cog_complexity,
            "avg_cog_complexity_per_function": self.avg_cog_complexity_per_function,
            "cognitive_complexity_segment": Segmentor.get_complexity_segment(
                self.avg_cog_complexity_per_function
            ),
        }

    @staticmethod
    def from_dict(data: dict) -> Self:
        metrics = FileMetrics(
            full_name=data["full_name"],
            loc=data["loc"],
            totalCc=data["totalCc"],
            avgCcPerFunction=data["avgCcPerFunction"],
            maintainabilityIndex=data["maintainabilityIndex"],
            avgLocPerFunction=data["avgLocPerFunction"],
            class_nodes=[ClassNode.from_dict(d) for d in data["class_nodes"]],
            function_nodes=[FunctionNode.from_dict(d) for d in data["function_nodes"]],
            import_name=data.get("import_name"),
            imports=data.get("imports"),
            code_smells=[CodeSmell.from_dict(d) for d in data.get("code_smells", [])],
            total_cog_complexity=data.get("total_cog_complexity", 0),
            avg_cog_complexity_per_function=data.get(
                "avg_cog_complexity_per_function", 0
            ),
        )
        metrics.afferent_coupling = data.get("afferent_coupling", 0)
        metrics.efferent_coupling = data.get("efferent_coupling", 0)
        metrics.instability = data.get("instability", 0)
        return metrics
