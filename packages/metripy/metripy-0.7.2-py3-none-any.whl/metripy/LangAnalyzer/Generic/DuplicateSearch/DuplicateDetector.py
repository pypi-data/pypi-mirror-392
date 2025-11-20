from typing import Dict, List

from simhash import Simhash

from metripy.LangAnalyzer.Generic.DuplicateSearch.CodeChunk import CodeChunk
from metripy.LangAnalyzer.Generic.DuplicateSearch.Tokenizer import Tokenizer


class DuplicateDetector:
    def __init__(
        self,
        tokenizer: Tokenizer | None = None,
        chunk_size: int = 5,
        min_lines: int = 3,
    ):
        """
        Initialize duplicate detector with chunking parameters.

        Args:
            tokenizer: Tokenizer to use for code tokenization
            chunk_size: Number of lines per chunk (sliding window size)
            min_lines: Minimum number of non-empty lines to consider a chunk
        """
        self.tokenizer = tokenizer or Tokenizer()
        self.chunks: List[CodeChunk] = []
        self.chunk_size = chunk_size
        self.min_lines = min_lines
        # TODO: improve this
        self.file_contents: Dict[str, str] = (
            {}
        )  # Store file contents for code extraction

    def compute_hash(self, code: str) -> Simhash:
        """Compute SimHash for a code string"""
        tokens = self.tokenizer.tokenize(code)
        if not tokens:
            return Simhash("")
        return Simhash(tokens)

    def add_code(self, filename: str, code: str) -> None:
        """
        Add code from a file and split it into chunks with location tracking.

        Args:
            filename: Path to the source file
            code: Full source code content
        """
        # Store file contents for later code extraction
        self.file_contents[filename] = code

        lines = code.split("\n")

        # Sliding window approach: create overlapping chunks
        for i in range(len(lines)):
            # Extract chunk
            end_idx = min(i + self.chunk_size, len(lines))
            chunk_lines = lines[i:end_idx]

            # Skip if chunk is too small
            if end_idx - i < self.min_lines:
                continue

            # Filter out empty/whitespace-only lines for meaningful content check
            non_empty = [line for line in chunk_lines if line.strip()]
            if len(non_empty) < self.min_lines:
                continue

            chunk_code = "\n".join(chunk_lines)

            # Skip chunks that are too simple (e.g., just braces)
            if len(chunk_code.strip()) < 20:
                continue

            hash_value = self.compute_hash(chunk_code)

            chunk = CodeChunk(
                filename=filename,
                start_line=i + 1,  # 1-indexed
                end_line=end_idx,  # 1-indexed
                code=chunk_code,
                hash_value=hash_value,
            )

            self.chunks.append(chunk)

    def _extract_code_lines(self, filename: str, start_line: int, end_line: int) -> str:
        """
        Extract code from a file between specified line numbers (1-indexed, inclusive).

        Args:
            filename: Path to the source file
            start_line: Starting line number (1-indexed)
            end_line: Ending line number (1-indexed, inclusive)

        Returns:
            Extracted code as a string
        """
        if filename not in self.file_contents:
            return ""

        lines = self.file_contents[filename].split("\n")
        # Convert to 0-indexed and extract the range
        start_idx = max(0, start_line - 1)
        end_idx = min(len(lines), end_line)

        return "\n".join(lines[start_idx:end_idx])

    def _do_ranges_overlap(
        self, start1: int, end1: int, start2: int, end2: int
    ) -> bool:
        """Check if two line ranges overlap"""
        return not (end1 < start2 or end2 < start1)

    def _are_duplicates_overlapping(self, dup1: Dict, dup2: Dict) -> bool:
        """
        Check if two duplicate reports are overlapping.
        They overlap if they involve the same file pair and their line ranges overlap.
        """
        # Check if they involve the same file pair (in either order)
        same_files = (
            dup1["file1"] == dup2["file1"] and dup1["file2"] == dup2["file2"]
        ) or (dup1["file1"] == dup2["file2"] and dup1["file2"] == dup2["file1"])

        if not same_files:
            return False

        # Check if line ranges overlap in both files
        if dup1["file1"] == dup2["file1"]:
            # Same file order
            overlap1 = self._do_ranges_overlap(
                dup1["start_line1"],
                dup1["end_line1"],
                dup2["start_line1"],
                dup2["end_line1"],
            )
            overlap2 = self._do_ranges_overlap(
                dup1["start_line2"],
                dup1["end_line2"],
                dup2["start_line2"],
                dup2["end_line2"],
            )
        else:
            # Reversed file order
            overlap1 = self._do_ranges_overlap(
                dup1["start_line1"],
                dup1["end_line1"],
                dup2["start_line2"],
                dup2["end_line2"],
            )
            overlap2 = self._do_ranges_overlap(
                dup1["start_line2"],
                dup1["end_line2"],
                dup2["start_line1"],
                dup2["end_line1"],
            )

        return overlap1 and overlap2

    def _merge_duplicates(self, dup1: Dict, dup2: Dict) -> Dict:
        """
        Merge two overlapping duplicate reports into one.
        Takes the maximum range from both duplicates.
        """
        # Ensure consistent file ordering
        if dup1["file1"] == dup2["file1"]:
            start_line1 = min(dup1["start_line1"], dup2["start_line1"])
            end_line1 = max(dup1["end_line1"], dup2["end_line1"])
            start_line2 = min(dup1["start_line2"], dup2["start_line2"])
            end_line2 = max(dup1["end_line2"], dup2["end_line2"])

            return {
                "file1": dup1["file1"],
                "start_line1": start_line1,
                "end_line1": end_line1,
                "file2": dup1["file2"],
                "start_line2": start_line2,
                "end_line2": end_line2,
                "similarity": max(dup1["similarity"], dup2["similarity"]),
                "code1": self._extract_code_lines(
                    dup1["file1"], start_line1, end_line1
                ),
                "code2": self._extract_code_lines(
                    dup1["file2"], start_line2, end_line2
                ),
                "lines": end_line1 - start_line1 + 1,
            }
        else:
            # Reversed order - normalize to file1/file2
            start_line1 = min(dup1["start_line1"], dup2["start_line2"])
            end_line1 = max(dup1["end_line1"], dup2["end_line2"])
            start_line2 = min(dup1["start_line2"], dup2["start_line1"])
            end_line2 = max(dup1["end_line2"], dup2["end_line1"])

            return {
                "file1": dup1["file1"],
                "start_line1": start_line1,
                "end_line1": end_line1,
                "file2": dup1["file2"],
                "start_line2": start_line2,
                "end_line2": end_line2,
                "similarity": max(dup1["similarity"], dup2["similarity"]),
                "code1": self._extract_code_lines(
                    dup1["file1"], start_line1, end_line1
                ),
                "code2": self._extract_code_lines(
                    dup1["file2"], start_line2, end_line2
                ),
                "lines": end_line1 - start_line1 + 1,
            }

    def _aggregate_overlapping_duplicates(self, duplicates: List[Dict]) -> List[Dict]:
        """
        Aggregate overlapping duplicate reports into larger consolidated reports.
        """
        if not duplicates:
            return []

        # Sort by file pairs and starting lines for easier processing
        sorted_dups = sorted(
            duplicates,
            key=lambda d: (d["file1"], d["file2"], d["start_line1"], d["start_line2"]),
        )

        aggregated = []
        current = sorted_dups[0].copy()

        for next_dup in sorted_dups[1:]:
            if self._are_duplicates_overlapping(current, next_dup):
                # Merge with current
                current = self._merge_duplicates(current, next_dup)
            else:
                # Save current and start new group
                aggregated.append(current)
                current = next_dup.copy()

        # Don't forget the last one
        aggregated.append(current)

        # Sort by similarity again (highest first)
        aggregated.sort(key=lambda x: x["similarity"], reverse=True)

        return aggregated

    def get_duplicates(self, min_similarity: float = 85.0) -> List[Dict]:
        """
        Find duplicate code chunks across all added files.
        Overlapping duplicate regions are automatically merged into single reports.

        Args:
            min_similarity: Minimum similarity percentage (0-100) to report as duplicate

        Returns:
            List of dictionaries containing duplicate information with locations
        """
        duplicates = []

        # Compare all chunk pairs
        for i in range(len(self.chunks)):
            for j in range(i + 1, len(self.chunks)):
                chunk1 = self.chunks[i]
                chunk2 = self.chunks[j]
                if chunk1.filename == chunk2.filename:
                    continue

                # Calculate Hamming distance
                distance = chunk1.hash_value.distance(chunk2.hash_value)
                similarity = (1 - distance / 64) * 100

                if similarity >= min_similarity:
                    duplicates.append(
                        {
                            "file1": chunk1.filename,
                            "start_line1": chunk1.start_line,
                            "end_line1": chunk1.end_line,
                            "file2": chunk2.filename,
                            "start_line2": chunk2.start_line,
                            "end_line2": chunk2.end_line,
                            "similarity": round(similarity, 2),
                            "code1": chunk1.code,
                            "code2": chunk2.code,
                            "lines": chunk1.end_line - chunk1.start_line + 1,
                        }
                    )

        # Sort by similarity (highest first)
        duplicates.sort(key=lambda x: x["similarity"], reverse=True)

        # Always aggregate overlapping duplicates
        duplicates = self._aggregate_overlapping_duplicates(duplicates)

        return duplicates
