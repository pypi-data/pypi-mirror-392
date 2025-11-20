import argparse
import asyncio
import dataclasses
from pathlib import Path
from typing import AsyncIterator

from import_completer.path_resolver import (
    convert_path_to_module_name,
)
from import_completer.types import ImportStatement

from loguru import logger


@dataclasses.dataclass
class TagDefinition:
    name: str
    file_path: Path
    pattern: str
    kind: str
    fields: list[str]

    @classmethod
    def parse_line(cls, line: str) -> 'TagDefinition':
        parts = line.split('\t')
        assert len(parts) >= 4

        tag = parts[0]
        file_path = parts[1]
        pattern = parts[2]
        kind = parts[3]
        fields = parts[4:]
        
        return cls(
            name=tag,
            file_path=Path(file_path).absolute().resolve(),
            pattern=pattern,
            kind=kind,
            fields=fields,
        )

    @property
    def source_file_extension(self) -> str:
        return self.file_path.suffix

    def get_module_path(self) -> Path:
        if self.file_path.with_suffix('').name == '__init__':
            return self.file_path.parent
        return self.file_path.with_suffix('')

    def match_field(self, field_value: str) -> bool:
        for field in self.fields:
            if field.startswith(field_value):
                return True
        return False

    def to_import_statement(self, paths_with_scores: list[tuple[Path, int]]) -> ImportStatement:
        module_path = self.get_module_path()
        for import_path, score in paths_with_scores:
            abs_import_path = import_path.absolute()
            if not module_path.is_relative_to(abs_import_path):
                continue

            relative_path = module_path.relative_to(abs_import_path)
            dotted_path = convert_path_to_module_name(relative_path)
            logger.debug(
                "Found import statement for name {} ({}) within path {}: {} [score: {}]",
                self.name, self.file_path, abs_import_path, dotted_path, score,
            )
            return ImportStatement(imported_from=dotted_path, symbol=self.name, score=score)
        else:
            raise ValueError(f"Could not find import statement for {module_path}")


async def get_matching_lines(pattern: str, tag_file: Path) -> list[str]:
    logger.debug("Executing 'look' command with pattern '{}' and at tag file: {}", pattern, tag_file)
    process = await asyncio.subprocess.create_subprocess_exec(
        'look', pattern, str(tag_file),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()
    assert process.returncode is not None
    if process.returncode == 1:
        logger.debug("No matching lines found.")
        return []
    elif process.returncode >= 2:
        raise Exception(
            f"Error: 'look' command failed with code '{process.returncode}',"
            f"\nstdout:\n{stdout.decode()}"
            f"\nstderr:\n{stderr.decode()}"
        )

    lines = stdout.decode().splitlines()
    logger.debug("Got {} matching lines.", len(lines))
    return lines


class TagsCompleter:
    def __init__(self, tag_files: list[Path], project_paths: list[Path], environment_paths: list[Path], stdlib_paths: list[Path]) -> None:
        self._tag_files = tag_files
        self._project_paths = project_paths
        self._environment_paths = environment_paths
        self._stdlib_paths = stdlib_paths
        self._paths_with_scores = [
            (path, 5) for path in self._project_paths
        ] + [
            (path, 3) for path in self._stdlib_paths
        ] + [
            (path, 1) for path in self._environment_paths
        ]

    async def get_matching_tags(self, pattern: str) -> AsyncIterator[tuple[TagDefinition, ImportStatement]]:
        tag_tasks: list[asyncio.Task] = []

        for tag_file in self._tag_files:
            if tag_file.exists():
                tag_tasks.append(
                    asyncio.create_task(get_matching_lines(pattern, tag_file))
                )

        for task in tag_tasks:
            lines = await task
            for line in lines:
                tag_definition = TagDefinition.parse_line(line)
                if not self.verify_tag_definition(tag_definition):
                    continue
                try:
                    import_statement = tag_definition.to_import_statement(self._paths_with_scores)
                except ValueError as exc:
                    logger.debug("Could not generate import statement for {}: {}", tag_definition, exc)
                    continue
                yield tag_definition, import_statement

    def verify_tag_definition(self, tag: TagDefinition) -> bool:
        if tag.source_file_extension not in {".py", ".pyi"}:
            return False
        if tag.match_field("class:") or tag.match_field("member:"):
            return False
        if tag.file_path.name.startswith("test_"):
            return False
        return True
