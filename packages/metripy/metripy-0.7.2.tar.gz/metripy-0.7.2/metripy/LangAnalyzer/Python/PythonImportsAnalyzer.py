import ast
from pathlib import Path


class PythonImportsAnalyzer:
    @staticmethod
    def extract_imports(code: str, project_root: str) -> list[str]:
        """Extract same-project imports from Python code.

        Args:
            code: The Python source code
            project_root: The project root package name to filter for

        Returns:
            List of import module names that belong to the same project
        """
        imports = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        # Check if it's a same-project import
                        if alias.name.startswith(project_root):
                            imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        # Check for same-project imports
                        if node.module.startswith(project_root):
                            imports.append(node.module)
                    # Handle relative imports (. or ..)
                    elif node.level > 0:
                        # Relative import within the project
                        imports.append("." * node.level + (node.module or ""))
        except SyntaxError:
            # If we can't parse the file, return empty list
            raise ValueError(f"Failed to parse code: {code}")
        return imports

    @staticmethod
    def extract_import_name(filename: str, project_root: str) -> str:
        """Extract the import name for the current module.

        Args:
            filename: The full file path
            project_root: The project root package name

        Returns:
            The import name for this module
        """
        path = Path(filename)

        # Get all parts of the path
        parts = path.parts

        # Find where the project root starts
        try:
            root_index = parts.index(project_root)
            # Get parts from project root onwards, excluding the file extension
            module_parts = list(parts[root_index:])
            # Remove .py extension from the last part
            module_parts[-1] = path.stem
            # Join with dots to create import name
            return ".".join(module_parts)
        except ValueError:
            raise ValueError(f"Failed to extract import name for {filename}")
