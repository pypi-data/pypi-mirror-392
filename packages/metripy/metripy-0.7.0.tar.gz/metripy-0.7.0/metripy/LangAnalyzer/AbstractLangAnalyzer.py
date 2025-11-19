from abc import ABC, abstractmethod

from metripy.Metric.Code.FileMetrics import FileMetrics
from metripy.Tree.ModuleNode import ModuleNode


class AbstractLangAnalyzer(ABC):
    def __init__(self):
        self.files: list[str] = []
        self.modules: dict[str, ModuleNode] = {}

    @abstractmethod
    def set_files(self, files: list[str]) -> None:
        raise NotImplementedError

    @abstractmethod
    def is_needed(self) -> bool:
        pass

    def before_run(self) -> None:
        # build cache
        pass

    def after_run(self) -> None:
        # clear cache
        pass

    @abstractmethod
    def get_lang_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def run(self) -> None:
        raise NotImplementedError

    @abstractmethod
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
