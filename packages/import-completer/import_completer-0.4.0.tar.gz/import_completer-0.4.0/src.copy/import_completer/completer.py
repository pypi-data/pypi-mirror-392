from typing import Iterable
from typing import NamedTuple

from loguru import logger

from import_completer.config import Config
from import_completer.tags_parser import TagsCompleter
from import_completer.types import ImportStatement, cleaned_import_statements
from import_completer.imports_cache import ImportsCacheCompleter


class ImportCompletion(NamedTuple):
    score: int
    import_statement: ImportStatement


class Completer:
    def __init__(self, config: Config):
        self._config = config
        self._tags_completer = TagsCompleter(
            tag_files=[self._config.project_tags, self._config.environment_tags],
            project_paths=self._config.project_paths,
            environment_paths=self._config.environment_paths,
            stdlib_paths=self._config.stdlib_paths,
        )
        self._imports_cache_completer = ImportsCacheCompleter(config)

    async def initialize_imports_cache(self) -> None:
        await self._imports_cache_completer.initialize()

    async def complete(self, pattern: str, exact_only: bool = False) -> Iterable[ImportStatement]:
        completions: list[ImportStatement] = []
        logger.info("Completing imports for pattern: {}", pattern)

        async for tag_definition, import_statement in self._tags_completer.get_matching_tags(pattern):
            if exact_only and import_statement.symbol != pattern:
                continue
            logger.trace("Found tag completion: {import_statement.symbol} ({import_statement.imported_from}) [score: {import_statement.score}]", import_statement=import_statement)
            completions.append(import_statement)

        for import_statement in self._imports_cache_completer.complete(pattern, exact_only):
            logger.trace("Found import cache completion: {import_statement.symbol} ({import_statement.imported_from}) [score: {import_statement.score}]", import_statement=import_statement)
            completions.append(import_statement)

        return cleaned_import_statements(completions)
