from typing import NamedTuple, Iterable, Iterator, Literal


class ScannedSymbol(NamedTuple):
    kind: Literal["variable", "function", "class"]  # TODO: add support for modules
    name: str
    parent_module: str
    metadata: dict
