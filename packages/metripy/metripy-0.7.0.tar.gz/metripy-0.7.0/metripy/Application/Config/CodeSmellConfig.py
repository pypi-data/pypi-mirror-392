class CodeSmellConfig:
    def __init__(self):
        self.config = {
            "unused_imports": True,
            "unused_functions": True,
            "too_many_parameters": True,
            "long_function": True,
            "snake_case_violation_variable": True,
            "snake_case_violation_function": True,
            "pascal_case_violation_class": True,
            "screaming_snake_case_violation_constant": True,
        }

    def disable_all(self) -> None:
        for param in self.config:
            self.config[param] = False

    def set(self, param: str, value: bool) -> None:
        if param in self.config.keys():
            self.config[param] = value

    def is_enabled(self, param: str) -> bool:
        return self.config.get(param, True)

    def to_dict(self) -> dict:
        return self.config
