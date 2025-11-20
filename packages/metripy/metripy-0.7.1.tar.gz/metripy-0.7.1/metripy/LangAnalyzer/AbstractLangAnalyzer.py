from abc import ABC, abstractmethod

from metripy.Metric.Code.FileMetrics import FileMetrics
from metripy.Tree.ModuleNode import ModuleNode
from metripy.Component.Output.ProgressBar import ProgressBar
from metripy.Application.Config.ProjectConfig import ProjectConfig
from metripy.LangAnalyzer.Generic.Metrics.LocAnalyzerFactory import LocAnalyzerFactory
from metripy.LangAnalyzer.Generic.Metrics.GenericLocAnalyzer import GenericLocAnalyzer
from metripy.LangAnalyzer.Generic.CodeSmell.CodeSmellDetectorFactory import CodeSmellDetectorFactory
from metripy.LangAnalyzer.Generic.Metrics.HalSteadAnalyzerFactory import HalSteadAnalyzerFactory
from metripy.LangAnalyzer.Generic.Metrics.GenericHalSteadAnalyzer import GenericHalSteadAnalyzer
from metripy.LangAnalyzer.Generic.DuplicateSearch.DuplicateDetector import DuplicateDetector
from metripy.LangAnalyzer.Generic.DuplicateSearch.TokenizerFactory import TokenizerFactory
from metripy.Tree.FunctionNode import FunctionNode

class AbstractLangAnalyzer(ABC):
    def __init__(self, project_config: ProjectConfig):
        self.config = project_config
        self.files: list[str] = []
        self.modules: dict[str, ModuleNode] = {}
        self.loc_analyzer: GenericLocAnalyzer = LocAnalyzerFactory.get_loc_analyzer(self.get_lang_name())
        self.halstead_analyzer: GenericHalSteadAnalyzer = HalSteadAnalyzerFactory.get_halstead_analyzer(self.get_lang_name())
        self.code_smell_detector = CodeSmellDetectorFactory.get_code_smell_detector(self.get_lang_name(), self.config.code_smells)
        self.duplicate_detector = DuplicateDetector(tokenizer=TokenizerFactory.get_tokenizer(self.get_lang_name()))


    # need to be implemented by sub analyzers
    @abstractmethod
    def get_lang_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_supported_extensions(self) -> tuple[str]:
        raise NotImplementedError

    # can be overridden by sub analyzers
    def before_run(self) -> None:
        # build cache
        pass

    def after_run(self) -> None:
        # clear cache
        pass

    def set_files(self, files: list[str]) -> None:
        self.files = list(filter(lambda file: file.endswith(self.get_supported_extensions()), files))

    def is_needed(self) -> bool:
        return len(self.files) > 0

    def run(self, progress_bar: ProgressBar) -> None:
        for file in self.files:
            with open(file, "r") as f:
                code = f.read()
                self.analyze(code, file)
            progress_bar.advance()

    def create_module_node(self, filename: str, code: str) -> ModuleNode:
        loc_data = self.loc_analyzer.analyze(code)
        full_name = self.full_name(filename)
        return ModuleNode(
            full_name,
            loc_data.get("loc", 0),
            loc_data.get("lloc", 0),
            loc_data.get("sloc", 0),
            loc_data.get("comments", 0),
            loc_data.get("multiline_comments", 0),
            loc_data.get("blank_lines", 0),
            loc_data.get("single_comments", 0),
        )

    def add_function_halstead_metrics(self, function_node: FunctionNode, function_code: str) -> None:
        function_metrics = self.halstead_analyzer.calculate_halstead_metrics(function_code)
        function_node.h1 = function_metrics["n1"]
        function_node.h2 = function_metrics["n2"]
        function_node.N1 = function_metrics["N1"]
        function_node.N2 = function_metrics["N2"]
        function_node.vocabulary = function_metrics["vocabulary"]
        function_node.length = function_metrics["length"]
        function_node.calculated_length = function_metrics["calculated_length"]
        function_node.volume = function_metrics["volume"]
        function_node.difficulty = function_metrics["difficulty"]
        function_node.effort = function_metrics["effort"]
        function_node.bugs = function_metrics["bugs"]
        function_node.time = function_metrics["time"]
        function_node.calc_mi()

    @staticmethod
    def full_name(
        filename: str, item_name: str | None = None, class_name: str | None = None
    ) -> str:
        if class_name is None:
            if item_name is None:
                return filename
            return f"{filename}:{item_name}"
        return f"{filename}:{class_name}:{item_name}"

    def get_metrics(self) -> list[FileMetrics]:
        metrics: dict[str, FileMetrics] = {}

        efferent_coupling = {}
        afferent_coupling = {}

        for module in self.modules.values():
            full_name = module.full_name

            if len(module.functions) > 0:
                totalCc = sum(function.complexity for function in module.functions)
                avgCcPerFunction = totalCc / len(module.functions)
                avgLocPerFunction = sum(
                    function.get_loc() for function in module.functions
                ) / len(module.functions)
                total_cog_complexity = sum(
                    function.cognitive_complexity for function in module.functions
                )
                avg_cog_complexity_per_function = total_cog_complexity / len(
                    module.functions
                )
            else:
                totalCc = 0
                avgCcPerFunction = 0
                avgLocPerFunction = 0
                total_cog_complexity = 0
                avg_cog_complexity_per_function = 0
            maintainabilityIndex = module.maintainability_index

            file_metric = FileMetrics(
                full_name=full_name,
                loc=module.loc,
                totalCc=totalCc,
                avgCcPerFunction=avgCcPerFunction,
                maintainabilityIndex=maintainabilityIndex,
                avgLocPerFunction=avgLocPerFunction,
                class_nodes=module.classes,
                function_nodes=module.functions,
                import_name=module.import_name,
                imports=module.imports,
                code_smells=module.code_smells,
                total_cog_complexity=total_cog_complexity,
                avg_cog_complexity_per_function=avg_cog_complexity_per_function,
            )
            metrics[full_name] = file_metric

            if not module.import_name or not module.imports:
                continue
            efferent_coupling[module.import_name] = len(module.imports)
            for import_name in module.imports:
                if import_name not in afferent_coupling:
                    afferent_coupling[import_name] = []
                afferent_coupling[import_name].append(module.import_name)

        for file_metric in metrics.values():
            imported_by = afferent_coupling.get(file_metric.import_name, [])
            ca = len(imported_by)
            ce = efferent_coupling.get(file_metric.import_name, 0)
            file_metric.imported_by = imported_by
            file_metric.afferent_coupling = ca
            file_metric.efferent_coupling = ce
            file_metric.instability = (ce / (ca + ce)) if (ca + ce) > 0 else 0

        return list(metrics.values())
