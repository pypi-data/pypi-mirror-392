from abc import ABC, abstractmethod
from typing import Dict


class GenericLocAnalyzer(ABC):
    """
    Abstract base class for multi-language LOC analysis.
    Subclasses must implement language-specific parsing logic.
    """

    def analyze(self, code: str) -> Dict[str, int]:
        lines = code.split("\n")
        stats = {
            "loc": len(lines),
            "sloc": 0,
            "lloc": 0,
            "comments": 0,
            "single_comments": 0,
            "multiline_comments": 0,
            "blank_lines": 0,
        }

        in_multiline_comment = False

        for line in lines:
            stripped = line.strip()

            if not stripped:
                stats["blank_lines"] += 1
                continue

            if in_multiline_comment:
                stats["multiline_comments"] += 1
                stats["comments"] += 1
                if self.is_multiline_comment_end(stripped):
                    in_multiline_comment = False
                continue

            if self.is_multiline_comment_start(stripped):
                in_multiline_comment = True
                stats["multiline_comments"] += 1
                stats["comments"] += 1
                # single line comment with mutliline markers
                if self.is_multiline_comment_end(stripped, True):
                    in_multiline_comment = False
                    stats["multiline_comments"] -= 1
                    stats["single_comments"] += 1
                continue

            if self.is_single_comment(stripped):
                stats["single_comments"] += 1
                stats["comments"] += 1
                continue

            # Count as source code
            stats["sloc"] += 1
            stats["lloc"] += self.count_logical_lines(stripped)

        return stats

    @abstractmethod
    def is_single_comment(self, line: str) -> bool:
        """Detect if a line is a single-line comment."""
        pass

    @abstractmethod
    def is_multiline_comment_start(self, line: str) -> bool:
        """Detect start of a multi-line comment."""
        pass

    @abstractmethod
    def is_multiline_comment_end(self, line: str, started_on_same_line: bool=False) -> bool:
        """Detect end of a multi-line comment."""
        pass

    @abstractmethod
    def count_logical_lines(self, line: str) -> int:
        """Count logical statements in a line (language-specific)."""
        pass
