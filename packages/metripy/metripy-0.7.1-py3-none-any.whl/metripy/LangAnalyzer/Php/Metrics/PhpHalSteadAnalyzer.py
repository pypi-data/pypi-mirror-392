from metripy.LangAnalyzer.Generic.Metrics.GenericHalSteadAnalyzer import GenericHalSteadAnalyzer


class PhpHalSteadAnalyzer(GenericHalSteadAnalyzer):
    def get_operators(self) -> list[str]:
        return [
            "+",
            "-",
            "*",
            "/",
            "%",
            "++",
            "--",
            "=",
            "==",
            "!=",
            "===",
            "!==",
            "<",
            ">",
            "<=",
            ">=",
            "&&",
            "||",
            "!",
            ".",
            "->",
            "=>",
            "::",
            "?",
            ":",
            "&",
            "|",
            "^",
            "~",
            "<<",
            ">>",
        ]
