"""Generic detector for unused imports across languages"""

from typing import List, Set

from metripy.LangAnalyzer.Generic.CodeSmell.CodeSmell import (
    CodeSmell,
    CodeSmellSeverity,
    CodeSmellType,
)
from metripy.LangAnalyzer.Generic.CodeSmell.Detectors.BaseDetector import (
    BaseCodeSmellDetector,
)


class UnusedImportsDetector(BaseCodeSmellDetector):
    """Detects unused imports in any language"""

    def detect(self) -> List[CodeSmell]:
        """Detect unused imports"""
        import_nodes = self.parser.get_import_nodes()
        if not import_nodes:
            return []

        # Get all used identifiers in the code
        used_identifiers = self._get_used_identifiers()

        for import_node in import_nodes:
            import_name = self.parser.extract_import_name(import_node)
            if not import_name:
                continue

            # Handle multiple imports in one statement
            import_names = [name.strip() for name in import_name.split(",")]

            for name in import_names:
                if name and name not in used_identifiers:
                    # Check if it's a module import and any attributes are used
                    is_used = any(
                        used.startswith(f"{name}.") for used in used_identifiers
                    )

                    if not is_used:
                        self.smells.append(
                            CodeSmell(
                                smell_type=CodeSmellType.UNUSED_IMPORT,
                                severity=CodeSmellSeverity.MINOR,
                                filename=self.filename,
                                line_number=self.get_line_number(import_node),
                                column=self.get_column(import_node),
                                code_line=self.parser.get_code_line(import_node),
                                message=f"Unused import '{name}'",
                                symbol=name,
                            )
                        )

        return self.smells

    def _get_used_identifiers(self) -> Set[str]:
        """Get all identifiers used in the code"""
        used = set()

        # Get all identifier nodes that are not in import statements
        all_identifiers = self.parser.get_identifier_nodes("usage")
        import_nodes = self.parser.get_import_nodes()

        # Build set of import node ranges to exclude
        import_ranges = set()
        for import_node in import_nodes:
            for node in self.parser.walk_tree(import_node):
                import_ranges.add((node.start_byte, node.end_byte))

        # Add identifiers that are not part of import statements
        for identifier in all_identifiers:
            node_range = (identifier.start_byte, identifier.end_byte)
            if node_range not in import_ranges:
                text = self.parser.get_node_text(identifier)
                if text:
                    used.add(text)

        return used
