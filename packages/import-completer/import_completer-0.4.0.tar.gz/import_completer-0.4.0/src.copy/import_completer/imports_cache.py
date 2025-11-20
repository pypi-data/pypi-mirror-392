import bisect
import asyncio
from pathlib import Path
from typing import Iterable, NamedTuple, Iterator

import tree_sitter_python as tspython
from tree_sitter import Language, Parser
from loguru import logger

from import_completer.config import Config
from import_completer.types import ImportStatement



PYTHON_LANGUAGE = Language(tspython.language())


class CachedImportStatement(NamedTuple):
    import_statement: ImportStatement
    file_path: Path


class ImportsCache:
    def __init__(self, config: Config):
        self._cached_imports: list[CachedImportStatement] = []

    async def load_project_imports(self, ignore_relative_imports: bool = True) -> None:
        logger.info("Loading project imports...")
        self._cached_imports = await discover_imports(Path.cwd().rglob("*.py"), ignore_relative_imports)
        self._cached_imports.sort()
        logger.info("Loaded {} project imports.", len(self._cached_imports))

    def find(self, pattern: str) -> Iterator[CachedImportStatement]:
        logger.debug("Searching for imports matching '{}'", pattern)
        begin = bisect.bisect_left(
            self._cached_imports,
            CachedImportStatement(
                import_statement=ImportStatement(symbol=pattern, imported_from=""), file_path=Path()
            )
        )
        for i in range(begin, len(self._cached_imports)):
            if not self._cached_imports[i].import_statement.symbol.startswith(pattern):
                break
            logger.trace("Found match: {}", self._cached_imports[i])
            yield self._cached_imports[i]


class ImportsCacheCompleter:
    def __init__(self, config: Config) -> None:
        self._config = config
        self._imports_cache = ImportsCache(config)
        self._initialized = False

    async def initialize(self) -> None:
        await self._imports_cache.load_project_imports()
        self._initialized = True

    def complete(self, pattern: str, exact_only: bool) -> list[ImportStatement]:
        if not self._initialized:
            logger.warning("Imports cache not initialized. Returning empty list.")
            return []

        results: list[ImportStatement] = []
        for cached_import in self._imports_cache.find(pattern):
            if exact_only and cached_import.import_statement.symbol != pattern:
                continue
            if results and results[-1] == cached_import.import_statement:
                continue
            results.append(cached_import.import_statement._replace(score=10))
        return results


def parse_import_statements_from_code(code: bytes, ignore_relative_imports: bool = True) -> list[ImportStatement]:
    parser = Parser()
    parser.language = PYTHON_LANGUAGE

    import_statements: list[ImportStatement] = []

    tree = parser.parse(code)
    root_node = tree.root_node

    def traverse(node):
        if node.type == 'import_from_statement':
            imported_from = node.named_children[0].text.decode("utf-8")
            if not imported_from.startswith('.') or not ignore_relative_imports:
                for imported_symbol in node.named_children[1:]:
                    import_statements.append(
                        ImportStatement(
                            imported_from=node.named_children[0].text.decode("utf-8"),
                            symbol=imported_symbol.text.decode("utf-8"),
                        )
                    )
        for child in node.children:
            traverse(child)

    traverse(root_node)
    return import_statements


def parse_import_statements_from_file(path: Path, ignore_relative_imports: bool = True) -> list[CachedImportStatement]:
    logger.info("Parsing imports from file: {}", path)
    with open(path, 'rb') as fh:
        parsed_imports = parse_import_statements_from_code(fh.read())
    logger.info("Imports found in '{}': {}", path, len(parsed_imports))
    return [
        CachedImportStatement(import_statement=import_statement, file_path=path)
        for import_statement in parsed_imports
    ]


async def discover_imports(paths: Iterable[Path], ignore_relative_imports: bool = True) -> list[CachedImportStatement]:
    loop = asyncio.get_running_loop()
    futures: list[asyncio.Future[list[CachedImportStatement]]] = []

    for path in paths:
        futures.append(
            loop.run_in_executor(None, parse_import_statements_from_file, path, ignore_relative_imports)
        )

    import_statements: list[CachedImportStatement] = []
    try:
        for awaitable in asyncio.as_completed(futures, timeout=15):
            import_statements.extend(await awaitable)
    except Exception:
        logger.exception("Error while discovering imports.")
        for future in futures:
            future.cancel()
    return import_statements


async def main():
    cached_imports = await discover_imports(
        Path.cwd().rglob("*.py")
    )
    print("Found imports:")
    for ci in cached_imports:
        print(f" * from {ci.import_statement.imported_from} import {ci.import_statement.symbol}")


if __name__ == "__main__":
    asyncio.run(main())
