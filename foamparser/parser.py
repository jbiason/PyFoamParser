import logging

from typing import Any
from typing import Dict
from typing import List

from .exceptions import UnexpectedCharacterError
from .exceptions import UnexpectedTokenError
from .tokenizer import FoamLexer
from .sly.lex import LexError


logger = logging.getLogger(__name__)


def parse(input: str) -> Dict[str, Any]:
    """Parse a Foam content, returning the dictionary with the data."""
    lexer = FoamLexer()
    tokens = lexer.tokenize(input)
    return proc_dict(tokens)


def proc_dict(tokens) -> Dict[str, Any]:
    result = {}
    entry = None
    values = []
    try:
        for token in tokens:
            logger.debug(
                "[D] token=%s, value=%s (entry=%s)", token.type, token.value, entry
            )

            if entry is None and token.type in [
                "LIST_START",
                "DICT_START",
                "END",
            ]:
                # To start a list, or dict, or to complete the values of something,
                # we need to have started something already.
                raise UnexpectedTokenError(token.value)
            elif token.type == "LIST_END":
                # we don't expect the end of a list while processing a dictionary
                raise UnexpectedTokenError(token.value)
            elif token.type == "DICT_END":
                break
            elif token.type == "IDENTIFIER":
                if entry is None:
                    entry = token.value
                else:
                    values.append(token.value)
            elif token.type == "QUOTED_STRING":
                if entry is None:
                    entry = token.value[1:-1]
                else:
                    values.append(token.value[1:-1])
            elif token.type == "LIST_START":
                values.append(proc_list(tokens))
            elif token.type == "DICT_START":
                inner_dict = proc_dict(tokens)
                result[entry] = inner_dict
                values = []
                entry = None
            elif token.type == "END":
                if len(values) == 1:
                    # this is just to make things prettier
                    result[entry] = values[0]
                else:
                    result[entry] = values
                entry = None
                values = []
    except LexError as exc:
        raise UnexpectedCharacterError(exc.text[:10], exc.error_index)

    return result


def proc_list(tokens) -> List[Any]:
    result = []
    for token in tokens:
        logger.debug("[L] token=%s, value=%s", token.type, token.value)
        if token.type in ["DICT_END", "END"]:
            raise UnexpectedTokenError(token.value)
        elif token.type == "IDENTIFIER":
            result.append(token.value)
        elif token.type == "DICT_START":
            result.append(proc_dict(tokens))
        elif token.type == "LIST_START":
            result.append(proc_list(tokens))
        elif token.type == "LIST_END":
            break
    return result
