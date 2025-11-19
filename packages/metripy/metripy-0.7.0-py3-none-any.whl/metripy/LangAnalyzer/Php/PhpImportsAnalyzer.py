from metripy.LangAnalyzer.Php.Ast.PhpAstParser import PhpAstParser


class PhpImportsAnalyzer:
    def __init__(self, filename: str, code: str):
        self.filename = filename
        self.code = code
        self.parser = PhpAstParser()
        self.parser.parse(code)

    def extract_import_name(self) -> str:
        return self.parser.get_fqcn(self.filename).replace("\\", "\\\\")

    def extract_imports(self) -> list[str]:
        imports = []
        for node in self.parser.get_import_nodes():
            imports.append(self.parser.extract_import_name(node))
        return imports
