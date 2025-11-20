from simhash import Simhash


class CodeChunk:
    """Represents a chunk of code with location information"""

    def __init__(
        self,
        filename: str,
        start_line: int,
        end_line: int,
        code: str,
        hash_value: Simhash,
    ):
        self.filename = filename
        self.start_line = start_line
        self.end_line = end_line
        self.code = code
        self.hash_value = hash_value

    def __repr__(self):
        return f"CodeChunk({self.filename}:{self.start_line}-{self.end_line})"
