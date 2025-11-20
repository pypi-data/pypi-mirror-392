from metripy.LangAnalyzer.Generic.DuplicateSearch.Tokenizer import Tokenizer
from metripy.LangAnalyzer.Php.DuplicateSearch.PhpTokenizer import PhpTokenizer
from metripy.LangAnalyzer.Python.DuplicateSearch.PythonTokenizer import PythonTokenizer


class TokenizerFactory:
    _TOKENIZERS = {
        "Python": PythonTokenizer(),
        "PHP": PhpTokenizer(),
        "Typescript": None,
    }

    @staticmethod
    def get_tokenizer(language: str) -> Tokenizer:
        try:
            return TokenizerFactory._TOKENIZERS[language]
        except KeyError:
            raise ValueError(f"No tokenizer found for language: {language}")
