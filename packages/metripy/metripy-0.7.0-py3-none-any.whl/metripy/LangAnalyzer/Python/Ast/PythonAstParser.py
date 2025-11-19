"""Python-specific AST parser implementation using tree-sitter"""

from typing import List, Optional

from tree_sitter import Node

from metripy.LangAnalyzer.Generic.CodeSmell.AstParser import AstParser


class PythonAstParser(AstParser):
    """Python-specific implementation of AST parser"""

    def __init__(self):
        super().__init__("python")

    def get_import_nodes(self) -> List[Node]:
        """Get all import statements"""
        imports = self.find_nodes_by_type("import_statement")
        imports.extend(self.find_nodes_by_type("import_from_statement"))
        return imports

    def get_function_nodes(self) -> List[Node]:
        """Get all function definitions"""
        return self.find_nodes_by_type("function_definition")

    def get_class_nodes(self) -> List[Node]:
        """Get all class definitions"""
        return self.find_nodes_by_type("class_definition")

    def get_variable_assignment_nodes(self) -> List[Node]:
        """Get all assignment statements"""
        return self.find_nodes_by_type("assignment")

    def get_identifier_nodes(self, context: str = "usage") -> List[Node]:
        """Get identifier nodes based on context"""
        return self.find_nodes_by_type("identifier")

    def extract_function_name(self, node: Node) -> Optional[str]:
        """Extract function name from function_definition node"""
        for child in node.children:
            if child.type == "identifier":
                return self.get_node_text(child)
        return None

    def extract_class_name(self, node: Node) -> Optional[str]:
        """Extract class name from class_definition node"""
        for child in node.children:
            if child.type == "identifier":
                return self.get_node_text(child)
        return None

    def extract_variable_name(self, node: Node) -> Optional[str]:
        """Extract variable name from assignment node"""
        # In Python, assignment structure is: left = right
        # The left side contains the identifier
        for child in node.children:
            if child.type == "identifier":
                return self.get_node_text(child)
            elif child.type in ("pattern_list", "tuple_pattern"):
                # Handle tuple unpacking: a, b = ...
                names = []
                for grandchild in child.children:
                    if grandchild.type == "identifier":
                        names.append(self.get_node_text(grandchild))
                return ", ".join(names) if names else None
        return None

    def extract_import_name(self, node: Node) -> Optional[str]:
        """Extract imported name from import node"""
        name = self.extract_import_qualified_name(node)
        if name:
            return name.split(".")[-1]
        return None

    def extract_import_qualified_name(self, node: Node) -> Optional[str]:
        """Extract imported module/name from import node"""
        if node.type == "import_statement":
            # import foo or import foo as bar
            for child in node.children:
                if child.type == "dotted_name":
                    return self.get_node_text(child)
                elif child.type == "aliased_import":
                    # Get the alias name
                    for grandchild in child.children:
                        if (
                            grandchild.type == "identifier"
                            and grandchild.next_sibling is None
                        ):
                            return self.get_node_text(grandchild)
                    # If no alias, get the original name
                    for grandchild in child.children:
                        if grandchild.type == "dotted_name":
                            return self.get_node_text(grandchild)

        elif node.type == "import_from_statement":
            # from foo import bar or from foo import bar as baz
            imported_names = []
            for child in node.children:
                if (
                    child.type == "dotted_name"
                    and child.prev_sibling
                    and self.get_node_text(child.prev_sibling) == "import"
                ):
                    imported_names.append(self.get_node_text(child))
                elif child.type == "aliased_import":
                    for grandchild in child.children:
                        if (
                            grandchild.type == "identifier"
                            and grandchild.next_sibling is None
                        ):
                            imported_names.append(self.get_node_text(grandchild))
                            break
                    else:
                        for grandchild in child.children:
                            if grandchild.type == "identifier":
                                imported_names.append(self.get_node_text(grandchild))
                                break
            return ", ".join(imported_names) if imported_names else None

        return None

    def get_function_parameters(self, function_node: Node) -> List[str]:
        """Extract parameter names from function definition"""
        params = []
        for child in function_node.children:
            if child.type == "parameters":
                for param_node in child.children:
                    if param_node.type == "identifier":
                        params.append(self.get_node_text(param_node))
                    elif param_node.type in ("typed_parameter", "default_parameter"):
                        # Handle typed and default parameters
                        for grandchild in param_node.children:
                            if grandchild.type == "identifier":
                                params.append(self.get_node_text(grandchild))
                                break
        return params
