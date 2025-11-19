import io
import token as token_module
import tokenize

from metripy.LangAnalyzer.Generic.DuplicateSearch.Tokenizer import Tokenizer


class PythonTokenizer(Tokenizer):
    """
    Python-specific tokenizer using Python's built-in tokenize module.
    Provides better accuracy for Python code by understanding Python syntax.
    """

    def __init__(self, normalize_identifiers: bool = False, ngram_size: int = 4):
        """
        Initialize Python tokenizer.

        Args:
            normalize_identifiers: If True, replace variable/function names with generic tokens
            ngram_size: Size of token n-grams to create (default: 4)
        """
        self.normalize_identifiers = normalize_identifiers
        self.ngram_size = ngram_size

    def tokenize(self, code: str) -> list[str]:
        """
        Tokenize Python code using Python's tokenize module.

        Args:
            code: Python source code string

        Returns:
            List of token n-grams
        """
        if not code.strip():
            return []

        try:
            # Use Python's tokenize module for accurate tokenization
            tokens = self._extract_tokens(code)

            # Create n-grams from tokens
            ngrams = self._create_ngrams(tokens)

            return ngrams
        except Exception:
            # Fallback to simple tokenization if parsing fails
            return self._fallback_tokenize(code)

    def _extract_tokens(self, code: str) -> list[str]:
        """
        Extract tokens from Python code, filtering out noise.

        Args:
            code: Python source code

        Returns:
            List of meaningful tokens
        """
        tokens = []

        # Tokenize using Python's tokenize module
        try:
            readline = io.StringIO(code).readline
            token_generator = tokenize.generate_tokens(readline)

            for tok in token_generator:
                tok_type = tok.type
                tok_string = tok.string

                # Skip whitespace, newlines, and encoding tokens
                if tok_type in (
                    token_module.NEWLINE,
                    token_module.NL,
                    token_module.INDENT,
                    token_module.DEDENT,
                    token_module.ENCODING,
                    token_module.ENDMARKER,
                ):
                    continue

                # Skip comments
                if tok_type == token_module.COMMENT:
                    continue

                # Normalize string literals to a generic token
                if tok_type == token_module.STRING:
                    # Preserve docstrings context but normalize content
                    tokens.append("STRING")
                    continue

                # Normalize number literals
                if tok_type == token_module.NUMBER:
                    tokens.append("NUMBER")
                    continue

                # Handle identifiers
                if tok_type == token_module.NAME:
                    if self.normalize_identifiers:
                        # Check if it's a keyword
                        if tok_string in (
                            "def",
                            "class",
                            "if",
                            "else",
                            "elif",
                            "for",
                            "while",
                            "try",
                            "except",
                            "finally",
                            "with",
                            "as",
                            "import",
                            "from",
                            "return",
                            "yield",
                            "pass",
                            "break",
                            "continue",
                            "raise",
                            "assert",
                            "lambda",
                            "and",
                            "or",
                            "not",
                            "is",
                            "in",
                            "None",
                            "True",
                            "False",
                        ):
                            tokens.append(tok_string)
                        else:
                            # Normalize identifiers
                            tokens.append("IDENTIFIER")
                    else:
                        tokens.append(tok_string)
                    continue

                # Add operators and other tokens as-is
                if tok_string.strip():
                    tokens.append(tok_string)

        except tokenize.TokenError:
            # Handle incomplete code gracefully
            pass

        return tokens

    def _create_ngrams(self, tokens: list[str]) -> list[str]:
        """
        Create n-grams from token list.

        Args:
            tokens: List of tokens

        Returns:
            List of n-gram strings
        """
        if len(tokens) < self.ngram_size:
            # If we have fewer tokens than ngram_size, return what we can
            if tokens:
                return [" ".join(tokens)]
            return []

        ngrams = []
        for i in range(len(tokens) - self.ngram_size + 1):
            ngram = " ".join(tokens[i : i + self.ngram_size])
            ngrams.append(ngram)

        return ngrams

    def _fallback_tokenize(self, code: str) -> list[str]:
        """
        Fallback tokenization when Python's tokenize module fails.
        Uses simple regex-based approach.

        Args:
            code: Python source code

        Returns:
            List of token n-grams
        """
        import re

        # Remove comments
        code = re.sub(r"#.*$", "", code, flags=re.MULTILINE)

        # Normalize strings
        code = re.sub(r'""".*?"""', "STRING", code, flags=re.DOTALL)
        code = re.sub(r"'''.*?'''", "STRING", code, flags=re.DOTALL)
        code = re.sub(r'"[^"]*"', "STRING", code)
        code = re.sub(r"'[^']*'", "STRING", code)

        # Tokenize by splitting on non-alphanumeric
        tokens = re.findall(r"\w+|[^\w\s]", code)
        tokens = [t for t in tokens if t.strip()]

        # Create n-grams
        return self._create_ngrams(tokens)
