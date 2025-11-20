from contextlib import asynccontextmanager
from typing import AsyncIterable
from import_completer.types import ScannedSymbol
from pathlib import Path
from import_completer.code_scanner import extract_symbols_from_origin
import sys
from typing import AsyncGenerator
from import_completer.path_discovery import get_internal_python_paths

from import_completer.symbols_database import DatabaseHandler

from loguru import logger


class CompletionEngine:
    def __init__(self, symbols_database: DatabaseHandler, origin_paths: list[Path]) -> None:
        self._symbols_database = symbols_database
        self._origin_paths = origin_paths
        self._is_fully_initialized = False

    @property
    def is_fully_initialized(self) -> bool:
        return self._is_fully_initialized

    async def initialize_database(self) -> None:
        self._symbols_database = DatabaseHandler()
        await self._symbols_database.__aenter__()
        await self._symbols_database.create_schema()
        await self._symbols_database.create_indices()
        self._symbols_database

    async def autoload_symbols(self) -> None:
        assert self._symbols_database is not None, "Database not initialized!"
        for origin_idx, path in enumerate((Path(p) for p in sys.path), 1):
            if not path.is_dir():
                continue
            logger.info("Rebuilding symbols for path: {}", path)
            await self._symbols_database.perform_rebuild_for_origin(origin_idx, extract_symbols_from_origin(path))
        self._is_fully_initialized = True

    async def lookup_symbol_prefix(self, prefix: str) -> AsyncIterable[ScannedSymbol]:
        assert self._symbols_database is not None, "Database not initialized!"
        async for symbol in self._symbols_database.lookup_symbol_name(prefix):
            yield symbol


@asynccontextmanager
async def create_completion_engine(origin_paths: list[Path]) -> AsyncGenerator[CompletionEngine, None]:
    symbols_database = DatabaseHandler()
    async with symbols_database:
        await symbols_database.create_schema()
        await symbols_database.create_indices()
        completion_engine = CompletionEngine(symbols_database, origin_paths)
        yield completion_engine


if __name__ == "__main__":
    import asyncio
    import sys

    async def _main():
        async with create_completion_engine(list(get_internal_python_paths())) as completion_engine:
            await completion_engine.autoload_symbols()
            print("Database fully initialized!")

            for word_to_complete in sys.argv[1:]:
                print(f"Completing for '{word_to_complete}':")
                async for symbol in completion_engine.lookup_symbol_prefix(word_to_complete):
                    print(f" - {symbol.kind}: {symbol.name} ({symbol.parent_module})")
                print()

    asyncio.run(_main())
