import re
from metripy.LangAnalyzer.Generic.DuplicateSearch.Tokenizer import Tokenizer


class PhpTokenizer(Tokenizer):
    """
    PHP-specific tokenizer using regex-based approach.
    Handles normalization of identifiers, strings, and numbers.
    """

    PHP_KEYWORDS = {
        "if", "else", "elseif", "endif", "for", "foreach", "while", "do",
        "switch", "case", "default", "break", "continue", "return", "function",
        "class", "interface", "trait", "extends", "implements", "namespace",
        "use", "public", "private", "protected", "static", "abstract", "final",
        "const", "global", "var", "echo", "print", "include", "require",
        "include_once", "require_once", "new", "try", "catch", "finally",
        "throw", "array", "true", "false", "null"
    }

    def __init__(self, normalize_identifiers: bool = False, ngram_size: int = 4):
        self.normalize_identifiers = normalize_identifiers
        self.ngram_size = ngram_size

    def tokenize(self, code: str) -> list[str]:
        if not code.strip():
            return []

        try:
            tokens = self._extract_tokens(code)
            return self._create_ngrams(tokens)
        except Exception:
            return []

    def _extract_tokens(self, code: str) -> list[str]:
        """
        Extract tokens using regex-based approach.
        """
        tokens = []

        # Remove PHP tags
        code = re.sub(r"<\?php|\?>", "", code)

        # Remove comments (single-line and multi-line)
        code = re.sub(r"//.*?$|#.*?$|/\*.*?\*/", "", code, flags=re.MULTILINE | re.DOTALL)

        # Normalize strings
        code = re.sub(r'"[^"]*"|\'[^\']*\'', "STRING", code)

        # Normalize numbers
        code = re.sub(r"\b\d+(\.\d+)?\b", "NUMBER", code)

        # Tokenize by splitting on non-alphanumeric characters
        raw_tokens = re.findall(r"\w+|[^\w\s]", code)

        for tok in raw_tokens:
            if tok.strip():
                if self.normalize_identifiers:
                    if tok in self.PHP_KEYWORDS:
                        tokens.append(tok)
                    elif re.match(r"^[A-Za-z_]\w*$", tok):  # identifier
                        tokens.append("IDENTIFIER")
                    else:
                        tokens.append(tok)
                else:
                    tokens.append(tok)

        return tokens

    def _create_ngrams(self, tokens: list[str]) -> list[str]:
        if len(tokens) < self.ngram_size:
            return [" ".join(tokens)] if tokens else []
        return [" ".join(tokens[i:i+self.ngram_size]) for i in range(len(tokens)-self.ngram_size+1)]
