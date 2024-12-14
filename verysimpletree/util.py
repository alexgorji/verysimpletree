from typing import Any


def make_list(input: Any) -> list[Any]:
    if isinstance(input, list):
        return input
    if isinstance(input, str):
        return [input]
    try:
        return list(input)
    except TypeError:
        return [input]