from typing import AsyncIterable
from import_completer.editor import AddLine
from typing import Iterable
from collections import defaultdict
from loguru import logger
from import_completer.types import ImportStatement

from pathlib import Path
from import_completer.completer import Completer
from import_completer.diagnostics import RuffDiagnostics


class ImportsFixer:
    def __init__(self, completer: Completer):
        self._completer = completer

    async def find_missing_imports_in_paths(self, paths: list[Path]) -> dict[Path, list[tuple[int, ImportStatement]]]:
        ruff_diagnostics = RuffDiagnostics()
        missing_symbols_map = await ruff_diagnostics.find_missing_imports_in_paths(paths)

        import_fixes: dict[Path, list[tuple[int, ImportStatement]]] = defaultdict(list)

        for path, symbols_list in missing_symbols_map.items():
            async for line, best_candidate in self._complete_import_statements(symbols_list):
                import_fixes[path].append((line, best_candidate))

        return import_fixes

    async def find_missing_imports_in_document(self, document: str) -> list[tuple[int, ImportStatement]]:
        ruff_diagnostics = RuffDiagnostics()
        missing_symbols = await ruff_diagnostics.find_missing_imports_in_document(document)

        import_fixes: list[tuple[int, ImportStatement]] = []

        async for line, best_candidate in self._complete_import_statements(missing_symbols):
            import_fixes.append((line, best_candidate))

        return import_fixes

    async def _complete_import_statements(
        self, missing_symbols: list[tuple[int, str]]
    ) -> AsyncIterable[tuple[int, ImportStatement]]:
        for line, symbol in missing_symbols:
            logger.debug("Found missing symbol: {}", symbol)
            candidates = await self._completer.complete(symbol, exact_only=True)
            best_candidate = next(iter(candidates), None)
            if best_candidate is None:
                logger.debug("No candidates found for symbol: {}", symbol)
            else:
                logger.debug("Found candidate for symbol: {} -> {}", symbol, best_candidate)
                yield (line, best_candidate)
        

def generate_changes_for_import_statements(import_statements: Iterable[ImportStatement]) -> list[AddLine]:
    changes = []
    for import_statement in import_statements:
        changes.append(
            AddLine(
                content=f"from {import_statement.imported_from} import {import_statement.symbol}",
            )
        )
    return changes
