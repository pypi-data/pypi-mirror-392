import re
from contextlib import AsyncExitStack
from typing import Any

from loguru import logger
from lsprotocol.types import (
    INITIALIZED,
    SHUTDOWN,
    TEXT_DOCUMENT_COMPLETION,
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    CompletionParams,
    InitializeParams,
    Position,
    ProgressParams,
    Range,
    TextEdit,
    WorkDoneProgressBegin,
    WorkDoneProgressEnd,
    WorkDoneProgressReport,
)
from pygls.lsp.server import LanguageServer

from import_completer.completion_engine import (
    CompletionEngine,
    create_completion_engine,
)
from import_completer.config import Config, get_version


def _handler_exception_wrapper(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception:
            logger.exception("Error occurred during handling of {}.", func.__name__)
            raise

    return wrapper


class ImportCompleterLanguageServer(LanguageServer):
    def __init__(self, *args: Any, config: Config, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._exit_stack = AsyncExitStack()
        self._config = config
        self._completion_engine: CompletionEngine | None = None

        self.feature(INITIALIZED)(
            _handler_exception_wrapper(self.initialize_completion_engine)
        )
        self.feature(TEXT_DOCUMENT_COMPLETION)(
            _handler_exception_wrapper(self.handle_completion)
        )
        self.feature(SHUTDOWN)(
            _handler_exception_wrapper(self.shutdown_completion_engine)
        )

    @property
    def completion_engine(self) -> CompletionEngine:
        assert self._completion_engine is not None, "Completion engine not initialized!"
        return self._completion_engine

    async def initialize_completion_engine(self, params: InitializeParams) -> None:
        logger.info("Initializing language server.")

        # Begin progress
        token = "import-completer-init"
        self.protocol.notify(
            "$/progress",
            ProgressParams(
                token=token,
                value=WorkDoneProgressBegin(
                    title="Import Completer", message="Initializing...", percentage=0
                ),
            ),
        )

        try:
            # Report progress - creating engine
            self.protocol.notify(
                "$/progress",
                ProgressParams(
                    token=token,
                    value=WorkDoneProgressReport(
                        message="Creating completion engine...", percentage=30
                    ),
                ),
            )

            self._completion_engine = await self._exit_stack.enter_async_context(
                create_completion_engine(self._config.origin_paths)
            )

            # Report progress - loading symbols
            self.protocol.notify(
                "$/progress",
                ProgressParams(
                    token=token,
                    value=WorkDoneProgressReport(
                        message="Loading symbols...", percentage=60
                    ),
                ),
            )

            await self._completion_engine.autoload_symbols()

            # End progress
            self.protocol.notify(
                "$/progress",
                ProgressParams(
                    token=token, value=WorkDoneProgressEnd(message="Ready!")
                ),
            )
            logger.info("Language server initialization complete.")

        except Exception:
            # End progress with error
            self.protocol.notify(
                "$/progress",
                ProgressParams(
                    token=token,
                    value=WorkDoneProgressEnd(message="Initialization failed"),
                ),
            )
            logger.exception("Failed to initialize language server")
            raise

    async def shutdown_completion_engine(self, params) -> None:
        """Clean up resources before server shutdown"""
        logger.info("Shutting down language server, cleaning up resources...")

        try:
            # Close all async context managers (including completion engine)
            await self._exit_stack.aclose()
            self._completion_engine = None
            logger.info("Resources cleaned up successfully.")
        except Exception:
            logger.exception("Error during shutdown cleanup")

        return None

    async def handle_completion(self, params: CompletionParams) -> CompletionList:
        logger.debug("Handling completion, with params: {}", params)
        document = self.workspace.get_text_document(params.text_document.uri)
        current_line = document.lines[params.position.line]
        last_word = re.split(
            r"[^a-zA-Z0-9_.]", current_line[: params.position.character]
        )[-1]
        logger.debug("Completing for word: '{}'", last_word)

        if "." in last_word:
            logger.debug("Ignoring completions for dotted names.")
            return CompletionList(is_incomplete=False, items=[])

        completions = [
            symbol
            async for symbol in self.completion_engine.lookup_symbol_prefix(last_word)
        ]

        items = []
        for symbol in completions:
            match symbol.kind:
                case "variable":
                    kind = CompletionItemKind.Variable
                case "function":
                    kind = CompletionItemKind.Function
                case "class":
                    kind = CompletionItemKind.Class
                case _:
                    kind = CompletionItemKind.Text
            items.append(
                CompletionItem(
                    label=symbol.name,
                    detail=f"from {symbol.parent_module} import {symbol.name}\n# import_completer",
                    kind=kind,
                    additional_text_edits=[
                        TextEdit(
                            new_text=f"from {symbol.parent_module} import {symbol.name}\n",
                            range=Range(
                                start=Position(line=0, character=0),
                                end=Position(line=0, character=0),
                            ),
                        ),
                    ],
                ),
            )

        logger.debug("Generated {} completions.", len(items))
        return CompletionList(is_incomplete=False, items=items)


def start_server():
    server = ImportCompleterLanguageServer(
        "import-completer", get_version(), config=Config.default()
    )
    logger.info("Starting ImportCompleter language server...")
    server.start_io()


if __name__ == "__main__":
    start_server()
