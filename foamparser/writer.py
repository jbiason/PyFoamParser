from typing import Any
from typing import Dict
from typing import List


from .exceptions import InvalidRootElementError


def write(input: Dict[str, Any]) -> str:
    """Write a Python dictionary into Foam."""
    if not isinstance(input, dict):
        raise InvalidRootElementError()

    output = []
    proc_dict(input, output, 0)
    return "\n".join(output)


def proc_dict(input: Dict[str, Any], output: List[str], level: int):
    space = spacing(level)
    for entry, value in input.items():
        if isinstance(value, dict):
            if not value:
                # an empty dictionary does not need linebreaks
                # XXX I'm not quite sure if we should output anything
                #     anyway in this case (e.g., the entry should not
                #     appear in the resulting file in this case). For
                #     now, we are using an empty dictionary.
                output.append(f"{space}{safe_value(entry)} {{}}")
            else:
                output.append(f"{space}{safe_value(entry)}")
                output.append(f"{space}{{")
                proc_dict(value, output, level + 1)
                output.append(f"{space}}}")
        elif isinstance(value, list):
            items = " ".join(safe_value(v) for v in value)
            output.append(f"{space}{safe_value(entry)} ( {items} );")
        else:
            output.append(f"{space}{safe_value(entry)} {safe_value(value)};")


def spacing(level: int) -> str:
    return " " * (level * 4)


def safe_value(value: str) -> str:
    if value is None:
        # XXX I'm not quite sure if we should output anything anyway in this
        #     this case. For now, we are showing an empty string.
        return '""'
    elif not isinstance(value, str):
        return value

    value = value.replace("\n", "\\n")
    if not value or any(char in [" ", "\\n", "-", ".", ":"] for char in value):
        return f'"{value}"'
    return value
