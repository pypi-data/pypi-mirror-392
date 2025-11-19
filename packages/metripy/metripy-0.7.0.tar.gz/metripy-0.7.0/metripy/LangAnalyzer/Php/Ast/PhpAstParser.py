from typing import List, Optional

from tree_sitter import Node

from metripy.LangAnalyzer.Generic.CodeSmell.AstParser import AstParser


class PhpAstParser(AstParser):
    def __init__(self):
        super().__init__("php")

    def get_fqcn(self, filename: str) -> str:
        namespace_nodes = self.find_nodes_by_type("namespace_definition")
        if len(namespace_nodes) == 0:
            return f"{filename}"
        namespace_node = namespace_nodes[0]
        namespace = None
        for child in self.walk_tree(namespace_node):
            if child.type == "namespace_name":
                namespace = self.get_node_text(child)
                break
        class_nodes = self.get_class_interface_trait_enum_nodes()
        if len(class_nodes) == 0:
            return f"{namespace}\\{filename}"
        class_node = class_nodes[0]
        class_name = None
        for child in class_node.children:
            if child.type == "name":
                class_name = self.get_node_text(child)
                if class_name:
                    break

        return f"{namespace}\\{class_name}"

    def get_import_nodes(self) -> List[Node]:
        return self.find_nodes_by_type("namespace_use_declaration")

    def get_function_nodes(self) -> List[Node]:
        return self.find_nodes_by_type("function_definition") + self.find_nodes_by_type(
            "method_declaration"
        )

    def get_class_nodes(self) -> List[Node]:
        return self.find_nodes_by_type("class_declaration")

    def get_interface_nodes(self) -> List[Node]:
        return self.find_nodes_by_type("interface_declaration")

    def get_trait_nodes(self) -> List[Node]:
        return self.find_nodes_by_type("trait_declaration")

    def get_enum_nodes(self) -> List[Node]:
        return self.find_nodes_by_type("enum_declaration")

    def get_class_interface_trait_enum_nodes(self) -> List[Node]:
        return (
            self.get_class_nodes()
            + self.get_interface_nodes()
            + self.get_trait_nodes()
            + self.get_enum_nodes()
        )

    def get_variable_assignment_nodes(self) -> List[Node]:
        return self.find_nodes_by_type("assignment_expression")

    # TODO: fix imports being used in docblocks, not yet recognized as usage
    def get_identifier_nodes(self, context: str = "usage") -> List[Node]:
        if context == "usage":
            return self.find_nodes_by_type("name")
        elif context == "definition":
            return self.find_nodes_by_type("variable_declarator")
        return []

    def extract_function_name(self, node: Node) -> Optional[str]:
        for child in node.children:
            if child.type == "name":
                return self.get_node_text(child)
        return None

    def extract_class_name(self, node: Node) -> Optional[str]:
        for child in node.children:
            if child.type == "name":
                return self.get_node_text(child)
        return None

    def extract_variable_name(self, node: Node) -> Optional[str]:
        for child in node.children:
            if child.type == "name":
                return self.get_node_text(child)
            elif child.type == "property_name":
                return self.get_node_text(child)
        return None

    def extract_import_qualified_name(self, node: Node) -> Optional[str]:
        for child in self.walk_tree(node):
            if child.type == "qualified_name":
                return self.get_node_text(child)
        return None

    def extract_import_name(self, node: Node) -> Optional[str]:
        name = None
        for child in self.walk_tree(node):
            if child.type == "name":
                name = self.get_node_text(child)
        return name

    def get_function_parameters(self, node: Node) -> List[str]:
        parameters = []
        for child in node.children:
            if child.type == "formal_parameters":
                for param_node in child.children:
                    if param_node.type == "name":
                        parameters.append(self.get_node_text(param_node))
        return parameters

    def get_class_properties(self, node: Node) -> List[str]:
        properties = []
        for child in node.children:
            if child.type == "property_declaration":
                for prop_node in child.children:
                    if prop_node.type == "name":
                        properties.append(self.get_node_text(prop_node))
        return properties

    def get_class_methods(self, node: Node) -> List[str]:
        methods = []
        for child in self.walk_tree(node):
            if child.type == "method_declaration":
                for method_node in child.children:
                    if method_node.type == "name":
                        methods.append(self.get_node_text(method_node))
        return methods

    def get_class_constants(self, node: Node) -> List[str]:
        constants = []
        for child in node.children:
            if child.type == "constant_declaration":
                for const_node in child.children:
                    if const_node.type == "name":
                        constants.append(self.get_node_text(const_node))
        return constants

    def get_class_interfaces(self, node: Node) -> List[str]:
        interfaces = []
        for child in node.children:
            if child.type == "interface_declaration":
                for interface_node in child.children:
                    if interface_node.type == "name":
                        interfaces.append(self.get_node_text(interface_node))
        return interfaces

    def get_class_traits(self, node: Node) -> List[str]:
        traits = []
        for child in node.children:
            if child.type == "trait_declaration":
                for trait_node in child.children:
                    if trait_node.type == "name":
                        traits.append(self.get_node_text(trait_node))
        return traits

    def get_class_abstract_classes(self, node: Node) -> List[str]:
        abstract_classes = []
        for child in node.children:
            if child.type == "abstract_class_declaration":
                for abstract_class_node in child.children:
                    if abstract_class_node.type == "name":
                        abstract_classes.append(self.get_node_text(abstract_class_node))
        return abstract_classes

    def get_class_final_classes(self, node: Node) -> List[str]:
        final_classes = []
        for child in node.children:
            if child.type == "final_class_declaration":
                for final_class_node in child.children:
                    if final_class_node.type == "name":
                        final_classes.append(self.get_node_text(final_class_node))
        return final_classes

    def get_class_magic_methods(self, node: Node) -> List[str]:
        magic_methods = []
        for child in node.children:
            if child.type == "magic_method_declaration":
                for magic_method_node in child.children:
                    if magic_method_node.type == "name":
                        magic_methods.append(self.get_node_text(magic_method_node))
        return magic_methods

    def get_class_static_methods(self, node: Node) -> List[str]:
        static_methods = []
        for child in node.children:
            if child.type == "static_method_declaration":
                for static_method_node in child.children:
                    if static_method_node.type == "name":
                        static_methods.append(self.get_node_text(static_method_node))
        return static_methods

    def get_class_private_methods(self, node: Node) -> List[str]:
        private_methods = []
        for child in node.children:
            if child.type == "private_method_declaration":
                for private_method_node in child.children:
                    if private_method_node.type == "name":
                        private_methods.append(self.get_node_text(private_method_node))
        return private_methods

    def get_class_protected_methods(self, node: Node) -> List[str]:
        protected_methods = []
        for child in node.children:
            if child.type == "protected_method_declaration":
                for protected_method_node in child.children:
                    if protected_method_node.type == "name":
                        protected_methods.append(
                            self.get_node_text(protected_method_node)
                        )
        return protected_methods

    def get_class_public_methods(self, node: Node) -> List[str]:
        public_methods = []
        for child in node.children:
            if child.type == "public_method_declaration":
                for public_method_node in child.children:
                    if public_method_node.type == "name":
                        public_methods.append(self.get_node_text(public_method_node))
        return public_methods

    def get_class_all_methods(self, node: Node) -> List[str]:
        return (
            self.get_class_methods(node)
            + self.get_class_magic_methods(node)
            + self.get_class_static_methods(node)
            + self.get_class_private_methods(node)
            + self.get_class_protected_methods(node)
            + self.get_class_public_methods(node)
        )

    def get_class_all_properties(self, node: Node) -> List[str]:
        return (
            self.get_class_properties(node)
            + self.get_class_constants(node)
            + self.get_class_interfaces(node)
            + self.get_class_traits(node)
            + self.get_class_abstract_classes(node)
            + self.get_class_final_classes(node)
        )

    def get_class_all_constants(self, node: Node) -> List[str]:
        return (
            self.get_class_constants(node)
            + self.get_class_interfaces(node)
            + self.get_class_traits(node)
            + self.get_class_abstract_classes(node)
            + self.get_class_final_classes(node)
        )

    def get_class_all_interfaces(self, node: Node) -> List[str]:
        return (
            self.get_class_interfaces(node)
            + self.get_class_traits(node)
            + self.get_class_abstract_classes(node)
            + self.get_class_final_classes(node)
        )

    def get_class_all_traits(self, node: Node) -> List[str]:
        return (
            self.get_class_traits(node)
            + self.get_class_abstract_classes(node)
            + self.get_class_final_classes(node)
        )

    def get_class_all_abstract_classes(self, node: Node) -> List[str]:
        return self.get_class_abstract_classes(node) + self.get_class_final_classes(
            node
        )

    def get_class_all_final_classes(self, node: Node) -> List[str]:
        return self.get_class_final_classes(node)
