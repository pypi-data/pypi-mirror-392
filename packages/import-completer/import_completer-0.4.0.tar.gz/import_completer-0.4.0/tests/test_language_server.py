import pytest
from lsprotocol.types import (
    CompletionParams,
    InitializeParams,
    Position,
    TextDocumentIdentifier,
)
from pygls.workspace import Workspace


@pytest.mark.asyncio
async def test_server_initialization(server_without_init):
    """Test that the server initializes properly"""
    server = server_without_init

    params = InitializeParams(
        capabilities={}, process_id=12345, root_uri="file:///test/workspace"
    )

    await server.initialize_completion_engine(params)

    assert server._completion_engine is not None
    assert server.completion_engine is not None

    # Cleanup
    await server.shutdown_completion_engine(None)


@pytest.mark.asyncio
async def test_completion_engine_property_assertion(server_without_init):
    """Test that accessing completion_engine before init raises assertion"""
    server = server_without_init

    with pytest.raises(AssertionError, match="Completion engine not initialized"):
        _ = server.completion_engine


@pytest.mark.asyncio
async def test_completion_empty_prefix(server):
    """Test completion with empty prefix"""
    # Initialize the server
    params = InitializeParams(capabilities={}, process_id=1, root_uri="file:///")
    await server.initialize_completion_engine(params)

    # Setup workspace with document
    server.workspace = Workspace(None, None)
    doc_uri = "file:///test/file.py"
    server.workspace.put_text_document(
        text_document=TextDocumentIdentifier(uri=doc_uri), source=""
    )

    # Request completion at empty position
    completion_params = CompletionParams(
        text_document=TextDocumentIdentifier(uri=doc_uri),
        position=Position(line=0, character=0),
    )

    result = await server.handle_completion(completion_params)

    assert result is not None
    assert isinstance(result.items, list)
    assert result.is_incomplete is False


@pytest.mark.asyncio
async def test_completion_with_prefix(server, monkeypatch):
    """Test completion with a symbol prefix"""

    # Mock symbol class
    class MockSymbol:
        def __init__(self, name, kind, parent_module):
            self.name = name
            self.kind = kind
            self.parent_module = parent_module

    async def mock_lookup(prefix):
        if prefix == "os":
            yield MockSymbol("os", "module", "builtins")
            yield MockSymbol("OrderedDict", "class", "collections")

    # Initialize server
    params = InitializeParams(capabilities={}, process_id=1, root_uri="file:///")
    await server.initialize_completion_engine(params)

    # Mock the lookup method
    monkeypatch.setattr(server.completion_engine, "lookup_symbol_prefix", mock_lookup)

    # Setup workspace
    server.workspace = Workspace(None, None)
    doc_uri = "file:///test/file.py"
    server.workspace.put_text_document(
        text_document=TextDocumentIdentifier(uri=doc_uri), source="os"
    )

    # Request completion
    completion_params = CompletionParams(
        text_document=TextDocumentIdentifier(uri=doc_uri),
        position=Position(line=0, character=2),
    )

    result = await server.handle_completion(completion_params)

    assert len(result.items) == 2
    assert result.items[0].label == "os"
    assert result.items[1].label == "OrderedDict"
    assert "from builtins import os" in result.items[0].detail
    assert "from collections import OrderedDict" in result.items[1].detail


@pytest.mark.asyncio
async def test_completion_ignores_dotted_names(server):
    """Test that completions are ignored for dotted attribute access"""
    # Initialize server
    params = InitializeParams(capabilities={}, process_id=1, root_uri="file:///")
    await server.initialize_completion_engine(params)

    # Setup workspace
    server.workspace = Workspace(None, None)
    doc_uri = "file:///test/file.py"
    server.workspace.put_text_document(
        text_document=TextDocumentIdentifier(uri=doc_uri), source="os.path"
    )

    # Request completion after dot
    completion_params = CompletionParams(
        text_document=TextDocumentIdentifier(uri=doc_uri),
        position=Position(line=0, character=7),  # after "os.path"
    )

    result = await server.handle_completion(completion_params)

    assert len(result.items) == 0
    assert result.is_incomplete is False


@pytest.mark.asyncio
async def test_completion_item_kinds(server, monkeypatch):
    """Test that different symbol kinds map to correct CompletionItemKind"""
    from lsprotocol.types import CompletionItemKind

    class MockSymbol:
        def __init__(self, name, kind, parent_module):
            self.name = name
            self.kind = kind
            self.parent_module = parent_module

    async def mock_lookup(prefix):
        yield MockSymbol("my_var", "variable", "test_module")
        yield MockSymbol("my_func", "function", "test_module")
        yield MockSymbol("MyClass", "class", "test_module")
        yield MockSymbol("unknown", "unknown_type", "test_module")

    # Initialize
    params = InitializeParams(capabilities={}, process_id=1, root_uri="file:///")
    await server.initialize_completion_engine(params)
    monkeypatch.setattr(server.completion_engine, "lookup_symbol_prefix", mock_lookup)

    # Setup workspace
    server.workspace = Workspace(None, None)
    doc_uri = "file:///test/file.py"
    server.workspace.put_text_document(
        text_document=TextDocumentIdentifier(uri=doc_uri), source="my"
    )

    # Request completion
    completion_params = CompletionParams(
        text_document=TextDocumentIdentifier(uri=doc_uri),
        position=Position(line=0, character=2),
    )

    result = await server.handle_completion(completion_params)

    assert len(result.items) == 4
    assert result.items[0].kind == CompletionItemKind.Variable
    assert result.items[1].kind == CompletionItemKind.Function
    assert result.items[2].kind == CompletionItemKind.Class
    assert result.items[3].kind == CompletionItemKind.Text  # unknown types become Text


@pytest.mark.asyncio
async def test_completion_adds_import_text_edit(server, monkeypatch):
    """Test that completion items include import text edits"""

    class MockSymbol:
        def __init__(self, name, kind, parent_module):
            self.name = name
            self.kind = kind
            self.parent_module = parent_module

    async def mock_lookup(prefix):
        yield MockSymbol("DataFrame", "class", "pandas")

    # Initialize
    params = InitializeParams(capabilities={}, process_id=1, root_uri="file:///")
    await server.initialize_completion_engine(params)
    monkeypatch.setattr(server.completion_engine, "lookup_symbol_prefix", mock_lookup)

    # Setup workspace
    server.workspace = Workspace(None, None)
    doc_uri = "file:///test/file.py"
    server.workspace.put_text_document(
        text_document=TextDocumentIdentifier(uri=doc_uri), source="Data"
    )

    # Request completion
    completion_params = CompletionParams(
        text_document=TextDocumentIdentifier(uri=doc_uri),
        position=Position(line=0, character=4),
    )

    result = await server.handle_completion(completion_params)

    assert len(result.items) == 1
    item = result.items[0]
    assert item.label == "DataFrame"
    assert item.additional_text_edits is not None
    assert len(item.additional_text_edits) == 1

    edit = item.additional_text_edits[0]
    assert edit.new_text == "from pandas import DataFrame\n"
    assert edit.range.start.line == 0
    assert edit.range.start.character == 0


@pytest.mark.asyncio
async def test_shutdown_cleans_up_resources(server):
    """Test that shutdown properly cleans up resources"""
    # Initialize
    params = InitializeParams(capabilities={}, process_id=1, root_uri="file:///")
    await server.initialize_completion_engine(params)

    assert server._completion_engine is not None

    # Shutdown
    await server.shutdown_completion_engine(None)

    assert server._completion_engine is None


@pytest.mark.asyncio
async def test_multiple_completions_on_same_line(server, monkeypatch):
    """Test completion at different positions on the same line"""

    class MockSymbol:
        def __init__(self, name, kind, parent_module):
            self.name = name
            self.kind = kind
            self.parent_module = parent_module

    async def mock_lookup_os(prefix):
        if prefix == "os":
            yield MockSymbol("os", "module", "builtins")

    async def mock_lookup_sys(prefix):
        if prefix == "sys":
            yield MockSymbol("sys", "module", "builtins")

    # Initialize
    params = InitializeParams(capabilities={}, process_id=1, root_uri="file:///")
    await server.initialize_completion_engine(params)

    # Setup workspace with line containing multiple words
    server.workspace = Workspace(None, None)
    doc_uri = "file:///test/file.py"
    server.workspace.put_text_document(
        text_document=TextDocumentIdentifier(uri=doc_uri), source="os sys"
    )

    # First completion at "os"
    monkeypatch.setattr(
        server.completion_engine, "lookup_symbol_prefix", mock_lookup_os
    )
    result1 = await server.handle_completion(
        CompletionParams(
            text_document=TextDocumentIdentifier(uri=doc_uri),
            position=Position(line=0, character=2),
        )
    )

    # Second completion at "sys"
    monkeypatch.setattr(
        server.completion_engine, "lookup_symbol_prefix", mock_lookup_sys
    )
    result2 = await server.handle_completion(
        CompletionParams(
            text_document=TextDocumentIdentifier(uri=doc_uri),
            position=Position(line=0, character=6),
        )
    )

    assert len(result1.items) == 1
    assert result1.items[0].label == "os"

    assert len(result2.items) == 1
    assert result2.items[0].label == "sys"
