import re


class Tokenizer:
    def tokenize(self, code: str) -> list[str]:
        """Simple token-based approach"""
        # Remove comments and strings for better matching
        code = re.sub(r"#.*$", "", code, flags=re.MULTILINE)
        code = re.sub(r"//.*$", "", code, flags=re.MULTILINE)
        code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
        code = re.sub(r'"[^"]*"', '""', code)
        code = re.sub(r"'[^']*'", "''", code)

        # Tokenize by splitting on non-alphanumeric
        tokens = re.findall(r"\w+|[^\w\s]", code)

        # Create n-grams (sliding window of 3 tokens)
        ngrams = []
        for i in range(len(tokens) - 2):
            ngrams.append(" ".join(tokens[i : i + 3]))

        return ngrams
