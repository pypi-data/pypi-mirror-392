from typing import AsyncIterable
from typing import NamedTuple
import re
from collections import defaultdict
import asyncio
import json
from pathlib import Path

from loguru import logger


class ExternalCommandError(Exception):
    pass


class _DiagnosticResult(NamedTuple):
    filename: str
    line: int
    symbol_name: str


class RuffDiagnostics:
    RE_UNDEFINED_NAME = re.compile(r"Undefined name `(\w+)`")

    async def find_missing_imports_in_paths(self, paths: list[Path]) -> dict[Path, list[tuple[int, str]]]:
        missing_symbols_map: dict[Path, list[tuple[int, str]]] = defaultdict(list)
        async for result in self._run_diagnostic_command([str(p) for p in paths]):
            missing_symbols_map[Path(result.filename)].append((result.line, result.symbol_name))

        return missing_symbols_map

    async def find_missing_imports_in_document(self, document: str) -> list[tuple[int, str]]:
        missing_symbols: list[tuple[int, str]] = []
        async for result in self._run_diagnostic_command(['-'], stdin_content=document):
            missing_symbols.append((result.line, result.symbol_name))

        return missing_symbols

    async def _run_diagnostic_command(self, args: list[str], stdin_content: str | None = None) -> AsyncIterable[_DiagnosticResult]:
        process = await asyncio.subprocess.create_subprocess_exec(
            'ruff', 'check', '--select', 'F821', '--output-format', 'json', *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE if stdin_content else None,
        )

        if stdin_content:
            assert process.stdin is not None
            process.stdin.write(stdin_content.encode())
            process.stdin.close()

        stdout, stderr = await process.communicate()
        assert process.returncode is not None
        if process.returncode not in (0, 1):
            raise ExternalCommandError(
                f"Error: command failed with code '{process.returncode}',"
                f"\nstdout:\n{stdout.decode()}"
                f"\nstderr:\n{stderr.decode()}"
            )

        found_errors = json.loads(stdout)
        for err in found_errors:
            line = err['location']['row'] - 1
            if match := self.RE_UNDEFINED_NAME.match(err['message']):
                missing_symbol = match.group(1)
                yield _DiagnosticResult(err['filename'], line, missing_symbol)
            else:
                logger.error("Failed to parse ruff error message: %s", err['message'])
