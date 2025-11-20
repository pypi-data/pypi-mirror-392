import re
from collections.abc import Generator, Iterator
from pathlib import Path
from typing import Literal

import tree_sitter_python as tspython
from tree_sitter import Language, Node, Parser

from import_completer.types import ScannedSymbol

PYTHON_TS_LANGUAGE = Language(tspython.language())
PYTHON_TS_PARSER = Parser()
PYTHON_TS_PARSER.language = PYTHON_TS_LANGUAGE

PYTHON_TOP_LEVEL_SYMBOLS_QUERY = PYTHON_TS_LANGUAGE.query(
    """
    [
      ; Direct module children
      (module
        (function_definition name: (identifier) @function-name))
      (module
        (class_definition name: (identifier) @class-name))
      (module
        (decorated_definition
          (function_definition name: (identifier) @function-name)))
      (module
        (decorated_definition
          (class_definition name: (identifier) @class-name)))
      (module
        (expression_statement
          (assignment left: (identifier) @assignment-name)))

      ; Inside top-level if statements
      (module
        (if_statement
          (block
            (function_definition name: (identifier) @function-name))))
      (module
        (if_statement
          (block
            (class_definition name: (identifier) @class-name))))
      (module
        (if_statement
          (block
            (decorated_definition
              (function_definition name: (identifier) @function-name)))))
      (module
        (if_statement
          (block
            (decorated_definition
              (class_definition name: (identifier) @class-name)))))
      (module
        (if_statement
          (block
            (expression_statement
              (assignment left: (identifier) @assignment-name)))))
      ; Else clause
      (module
        (if_statement
          (else_clause
            (block
              (function_definition name: (identifier) @function-name)))))
      (module
        (if_statement
          (else_clause
            (block
              (class_definition name: (identifier) @class-name)))))
      (module
        (if_statement
          (else_clause
            (block
              (decorated_definition
                (function_definition name: (identifier) @function-name))))))
      (module
        (if_statement
          (else_clause
            (block
              (decorated_definition
                (class_definition name: (identifier) @class-name))))))
      (module
        (if_statement
          (else_clause
            (block
              (expression_statement
                (assignment left: (identifier) @assignment-name))))))
    ]
    """
)

RE_PYTHON_VALID_MODULE_FILE_NAME = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*\.pyi?$")
RE_PYTHON_VALID_MODULE_DIRECTORY_NAME = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


def discover_python_modules(directory: str | Path) -> Generator[Path]:
    """
    Walk through directory and yield Python module files (.py and .pyi).
    Descends into subdirectories only if they are Python modules (contain __init__.py).

    Args:
        directory: Root directory to start scanning from

    Yields:
        Path objects for Python module files
    """

    directory = Path(directory)

    if not directory.is_dir():
        return

    for child_entity_path in directory.iterdir():
        if (
            child_entity_path.is_file()
            and RE_PYTHON_VALID_MODULE_FILE_NAME.match(child_entity_path.name)
            is not None
        ):
            yield child_entity_path
        elif (
            child_entity_path.is_dir()
            and RE_PYTHON_VALID_MODULE_DIRECTORY_NAME.match(child_entity_path.name)
            is not None
        ):
            # Recursively process subdirectories if they are Python packages
            if (child_entity_path / "__init__.py").exists() or (
                child_entity_path / "__init__.pyi"
            ).exists():
                yield from discover_python_modules(child_entity_path)
        else:
            pass
            # print(f"Skipping {child_entity_path}")


def extract_symbols_from_origin(origin_path: Path) -> Iterator[ScannedSymbol]:
    for module_path in discover_python_modules(origin_path):
        yield from extract_symbols_from_file(module_path, origin_path)


def extract_symbols_from_file(
    file_path: Path, origin_path: Path
) -> Iterator[ScannedSymbol]:
    """
    Extract all top-level symbols from a given Python file.
    """

    with open(file_path, "rb") as fh:
        source_code = fh.read()

    yield from extract_symbols(
        source_code, annotated_file_path=file_path, origin_path=origin_path
    )


def extract_symbols(
    source_code: bytes, annotated_file_path: Path, origin_path: Path
) -> Iterator[ScannedSymbol]:
    """
    Extract all top-level symbols from a given Python source code.
    """

    module_relative_path = Path(annotated_file_path.relative_to(origin_path))
    parent_module = ".".join(module_relative_path.with_suffix("").parts)

    def _make_scanned_symbol(
        kind: Literal["function", "class", "variable"], node: Node
    ) -> ScannedSymbol:
        assert node.text is not None
        return ScannedSymbol(
            kind=kind,
            name=node.text.decode("utf-8"),
            parent_module=parent_module,
            metadata={},
        )

    tree = PYTHON_TS_PARSER.parse(source_code)
    root_node = tree.root_node

    captures = PYTHON_TOP_LEVEL_SYMBOLS_QUERY.captures(root_node)
    for node in captures.get("function-name", []):
        if node.text:
            yield _make_scanned_symbol("function", node)

    for node in captures.get("class-name", []):
        if node.text:
            yield _make_scanned_symbol("class", node)

    for node in captures.get("assignment-name", []):
        if node.text:
            yield _make_scanned_symbol("variable", node)


if __name__ == "__main__":
    import sys

    for path in (Path(p) for p in sys.path):
        if not path.is_dir():
            continue
        for module_path in discover_python_modules(path):
            print(f"Discovered module: {module_path}")
            for symbol in extract_symbols_from_file(
                module_path, annotated_source_sys_path=path
            ):
                print(f"  + {symbol.kind}: {symbol.name}")
