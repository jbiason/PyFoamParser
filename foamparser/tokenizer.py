from .sly import Lexer


class FoamLexer(Lexer):
    tokens = {
        DICT_START,
        DICT_END,
        LIST_START,
        LIST_END,
        END,
        QUOTED_STRING,
        IDENTIFIER,
    }

    ignore = " \t\n"

    DICT_START = r"{"
    DICT_END = r"}"

    LIST_START = r"\("
    LIST_END = r"\)"

    END = ";"

    QUOTED_STRING = r'".*"'
    IDENTIFIER = r"[a-zA-Z0-9_]+"
