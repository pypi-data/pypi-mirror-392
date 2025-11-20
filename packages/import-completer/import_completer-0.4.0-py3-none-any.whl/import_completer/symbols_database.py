from collections.abc import AsyncIterable, Iterable
from pathlib import Path

import aiosqlite
from loguru import logger

from import_completer.types import ScannedSymbol

DB_SYMBOLS_NAME = "symbols"
DB_SYMBOLS_SCHEMA = [
    ("generation", "INTEGER"),
    ("kind", "TEXT"),
    ("name", "TEXT"),
    ("origin_index", "INTEGER"),
    ("parent_module", "TEXT"),
    ("metadata_json", "TEXT"),
]
DB_INDICES = [
    ("idx_symbols_name", DB_SYMBOLS_NAME, ["name"]),
    ("idx_symbols_parent_module", DB_SYMBOLS_NAME, ["origin_index", "parent_module"]),
]


class DatabaseHandler:
    def __init__(self, database_path: str | Path = ":memory:") -> None:
        self._database_path = database_path
        self._connection = None

    async def __aenter__(self):
        self._connection = await aiosqlite.connect(str(self._database_path))
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._connection:
            await self._connection.close()

    async def create_schema(self) -> None:
        assert self._connection is not None, "Database connection not initialized!"
        await self._connection.execute(
            f"CREATE TABLE IF NOT EXISTS {DB_SYMBOLS_NAME} ({', '.join(f'{name} {type}' for name, type in DB_SYMBOLS_SCHEMA)})"
        )
        await self._connection.commit()

    async def create_indices(self) -> None:
        assert self._connection is not None, "Database connection not initialized!"
        for index_name, table_name, index_columns in DB_INDICES:
            await self._connection.execute(
                f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({', '.join(index_columns)})"
            )
        await self._connection.commit()

    async def drop_indices(self) -> None:
        assert self._connection is not None, "Database connection not initialized!"
        for index_name, _, _ in DB_INDICES:
            await self._connection.execute(f"DROP INDEX IF EXISTS {index_name}")
        await self._connection.commit()

    async def perform_rebuild_for_origin(
        self, origin_index: int, symbols: Iterable[ScannedSymbol]
    ) -> None:
        assert self._connection is not None, "Database connection not initialized!"

        async with self._connection.cursor() as cursor:
            await cursor.execute("BEGIN")
            logger.info(f"Rebuilding symbols for origin_index: {origin_index}")
            await cursor.execute(
                f"""
                DELETE FROM {DB_SYMBOLS_NAME} WHERE origin_index = ?
                """,
                (origin_index,),
            )
            await cursor.executemany(
                """
                INSERT INTO symbols (generation, kind, name, origin_index, parent_module, metadata_json)
                VALUES (1, ?, ?, ?, ?, ?)
                """,
                (
                    (symbol.kind, symbol.name, origin_index, symbol.parent_module, "")
                    for symbol in symbols
                ),
            )
            logger.info(
                f"Added {cursor.rowcount} symbols for origin_index: {origin_index}"
            )
            await cursor.execute("COMMIT")

    async def lookup_symbol_name(self, name_part: str) -> AsyncIterable[ScannedSymbol]:
        assert self._connection is not None, "Database connection not initialized!"
        cursor = await self._connection.execute(
            """
            SELECT kind, name, parent_module
            FROM symbols
            WHERE name >= ? AND name < ?
            """,
            (f"{name_part}", f"{name_part}~"),
        )
        async for row in cursor:
            yield ScannedSymbol(*row, metadata={})
