import shutil
import tempfile
from pathlib import Path

import pytest

from import_completer.config import Config
from import_completer.language_server import ImportCompleterLanguageServer


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace directory with sample Python files"""
    temp_dir = tempfile.mkdtemp()
    workspace = Path(temp_dir)

    # Create some sample Python files
    (workspace / "module_a.py").write_text(
        """
class MyClass:
    def my_method(self):
        pass

def my_function():
    pass

MY_CONSTANT = 42
"""
    )

    (workspace / "module_b.py").write_text(
        """
from typing import List

def another_function(items: List[str]):
    return items
"""
    )

    yield workspace

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
async def server(temp_workspace):
    """Create a test server instance with temp workspace"""
    config = Config(origin_paths=[str(temp_workspace)])
    server = ImportCompleterLanguageServer("test-server", "1.0.0", config=config)

    yield server

    # Cleanup
    if server._completion_engine:
        await server.shutdown_completion_engine(None)


@pytest.fixture
def server_without_init(temp_workspace):
    """Create a test server instance without initialization"""
    config = Config(origin_paths=[str(temp_workspace)])
    server = ImportCompleterLanguageServer("test-server", "1.0.0", config=config)
    return server
