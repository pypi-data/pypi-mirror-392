from abc import ABC


class AbstractFormatter(ABC):

    COLORS = {
        "good": "32",  # Green
        "ok": "33",  # Yellow
        "warning": "38;2;255;165;0",  # Orange (TrueColor)
        "critical": "31",  # Red
    }

    def _format_row(self, col_widths: list[int], row: list[str]) -> str:
        return " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row))

    def format_table(self, headers: list[str], data: list[list[str]]) -> str:
        # Calculate column widths based on headers and data
        col_widths = [len(header) for header in headers]
        for row in data:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))

        # Build the table
        header_line = self._format_row(col_widths, headers)
        separator = "-+-".join("-" * width for width in col_widths)
        data_lines = [self._format_row(col_widths, row) for row in data]

        # Combine everything
        return "\n".join([header_line, separator] + data_lines)

    def colored_stacked_info(
        self, values: list[int], labels: list[str], colors: list[str], width: int = 50
    ) -> str:

        segments = len(values)
        segment_width = width // segments  # Equal width for each segment
        bar = ""

        for value, label, color in zip(values, labels, colors):
            text = f"{label}: {value}"
            # Truncate or pad text to fit segment width
            if len(text) > segment_width:
                text = text[:segment_width]
            else:
                text = text.center(segment_width)
            # Add colored segment
            bar += f"\033[{color}m{text}\033[0m"
        return bar

    def colored_stacked_bar(
        self, values: list[int], colors: list[str], width: int = 50
    ) -> str:
        total = sum(values)
        bar = ""
        for value, color in zip(values, colors):
            segment_length = int((value / total) * width)
            bar += f"\033[{color}m" + "█" * segment_length
        bar += "\033[0m"  # Reset color
        return bar
