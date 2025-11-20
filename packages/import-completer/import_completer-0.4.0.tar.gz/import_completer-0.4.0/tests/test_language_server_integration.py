import pytest
from lsprotocol.types import InitializeParams
from pygls.protocol import LanguageServerProtocol
from pygls.workspace import Workspace

from import_completer.config import Config
from import_completer.language_server import ImportCompleterLanguageServer


@pytest.mark.asyncio
async def test_full_lsp_lifecycle(temp_workspace):
    """Test complete lifecycle: initialize -> complete -> shutdown"""
    config = Config(origin_paths=[str(temp_workspace)])
    server = ImportCompleterLanguageServer("test", "1.0", config=config)

    # Create protocol
    protocol = LanguageServerProtocol(server)
    server.lsp = protocol

    # Mock transport
    class MockTransport:
        def write(self, data):
            pass

        def close(self):
            pass

    protocol.transport = MockTransport()

    # Initialize workspace
    server.workspace = Workspace(None, None)

    # Initialize
    params = InitializeParams(
        processId=1234, rootUri=f"file://{temp_workspace}", capabilities={}
    )

    await server.initialize_completion_engine(params)

    assert server._completion_engine is not None

    # Cleanup
    await server.shutdown_completion_engine(None)
    assert server._completion_engine is None


@pytest.mark.asyncio
async def test_server_handles_initialization_error_gracefully(temp_workspace):
    """Test that server handles initialization errors gracefully"""
    # Create config with non-existent path to trigger potential errors
    config = Config(origin_paths=["/non/existent/path"])
    server = ImportCompleterLanguageServer("test", "1.0", config=config)

    # Setup protocol and workspace
    protocol = LanguageServerProtocol(server)
    server.lsp = protocol

    class MockTransport:
        def write(self, data):
            pass

        def close(self):
            pass

    protocol.transport = MockTransport()
    server.workspace = Workspace(None, None)

    params = InitializeParams(processId=1234, rootUri="file:///test", capabilities={})

    # This might raise an exception depending on implementation
    # The test verifies that the server can handle initialization with invalid paths
    try:
        await server.initialize_completion_engine(params)
    except Exception:
        # If initialization fails, that's acceptable for invalid paths
        pass

    # Cleanup - should work even if initialization failed
    await server.shutdown_completion_engine(None)


@pytest.mark.asyncio
async def test_server_version_and_name():
    """Test that server has correct name and version"""
    config = Config(origin_paths=["."])
    server = ImportCompleterLanguageServer("test-server", "1.2.3", config=config)

    assert server.name == "test-server"
    assert server.version == "1.2.3"

    # Cleanup
    await server.shutdown_completion_engine(None)


@pytest.mark.asyncio
async def test_double_shutdown_is_safe(server):
    """Test that calling shutdown twice doesn't cause errors"""
    params = InitializeParams(processId=1, rootUri="file:///", capabilities={})
    await server.initialize_completion_engine(params)

    # First shutdown
    await server.shutdown_completion_engine(None)
    assert server._completion_engine is None

    # Second shutdown should be safe
    await server.shutdown_completion_engine(None)
    assert server._completion_engine is None


@pytest.mark.asyncio
async def test_shutdown_before_init_is_safe():
    """Test that shutdown before initialization doesn't cause errors"""
    config = Config(origin_paths=["."])
    server = ImportCompleterLanguageServer("test", "1.0", config=config)

    # Shutdown without initialization
    await server.shutdown_completion_engine(None)
    assert server._completion_engine is None
