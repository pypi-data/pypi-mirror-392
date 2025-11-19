import os

from metripy.Application.Config.Config import Config
from metripy.Component.Output.CliOutput import CliOutput
from metripy.Metric.ProjectMetrics import ProjectMetrics
from metripy.Tree.FunctionNode import FunctionNode


class Reporter:

    HEADERS = [
        "File",
        "Class",
        "Function",
        "LOC",
        "Cyclomatic Complexity",
        "Cognitive Complexity",
        "Maintainability Index",
        "Halstead h1",
        "Halstead h2",
        "Halstead n1",
        "Halstead n2",
        "Vocabulary",
        "Length",
        "Calculated Length",
        "Volume",
        "Difficulty",
        "Effort",
        "Time",
        "Bugs",
    ]

    def __init__(self, config: Config, output: CliOutput):
        self.config = config
        self.output = output

        self.delimiter = ","

        os.makedirs(os.path.dirname(self.config.path), exist_ok=True)
        self.file = open(self.config.path, "w")

    def __del__(self):
        self.file.close()

    def _write_line(self, data: list[str]):
        self.file.write(self.delimiter.join(data) + "\n")

    def generate(self, metrics: ProjectMetrics):
        self._write_line(self.HEADERS)

        data = []
        already_seen_functions = set()
        for file in metrics.file_metrics:
            for class_node in file.class_nodes:
                for function in class_node.functions:
                    data.append(
                        self.create_function_row(
                            file.full_name, class_node.full_name, function
                        )
                    )
                    already_seen_functions.add(function.full_name)
            # to catch global functions
            for function in file.function_nodes:
                if function.full_name in already_seen_functions:
                    continue
                data.append(self.create_function_row(file.full_name, "", function))
                already_seen_functions.add(function.full_name)

        for row in data:
            self._write_line(row)

    def create_function_row(
        self, file_name: str, class_name: str, function: FunctionNode
    ) -> list[str]:
        return [
            str(elem)
            for elem in [
                file_name,
                class_name,
                function.full_name,
                function.get_loc(),
                function.complexity,
                function.cognitive_complexity,
                function.maintainability_index,
                function.h1,
                function.h2,
                function.N1,
                function.N2,
                function.vocabulary,
                function.length,
                function.calculated_length,
                function.volume,
                function.difficulty,
                function.effort,
                function.time,
                function.bugs,
            ]
        ]
