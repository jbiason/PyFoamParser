from typing import Any
from typing import Dict


from .exceptions import InvalidRootElement


def write(input: Dict[str, Any]) -> str:
    """Write a Python dictionary into Foam."""
    if not isinstance(input, dict):
        raise InvalidRootElement

    output = []
    proc_dict(input, output, 0)
    return "\n".join(output)


def proc_dict(input: Dict[str, Any], output, level):
    space = spacing(level)
    for entry, value in input.items():
        if isinstance(value, dict):
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
    value = value.replace("\n", "\\n")
    if " " in value or "\\n" in value or "-" in value:
        return f'"{value}"'
    return value
