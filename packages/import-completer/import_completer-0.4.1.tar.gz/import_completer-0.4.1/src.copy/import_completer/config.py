from import_completer.path_discovery import discover_paths_for_python_executable
from import_completer.path_discovery import get_internal_python_paths
from pathlib import Path
import logging
import dataclasses
import argparse
from importlib.metadata import version, PackageNotFoundError

from loguru import logger


def get_version() -> str:
    """Get the package version from installed metadata, or 'dev' if not installed."""
    try:
        return version("import-completer")
    except PackageNotFoundError:
        return "dev"


@dataclasses.dataclass
class Config:
    origin_paths: list[Path]

    @classmethod
    def default(cls) -> 'Config':
        return cls(
            origin_paths=list(discover_paths_for_python_executable()),
        )
