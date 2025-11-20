import asyncio
import sys
from pathlib import Path
from typing import Iterator

from loguru import logger


async def generate_tags_for_paths(
    paths: list[Path],
    output_file: Path,
    *,
    ctags_executable: str = 'ctags',
    extra_args: list[str] | None = None,
) -> None:
    cmd_args = [
        '-f', str(output_file.expanduser()),
        '--languages=Python',
        '--map-Python=+.pyi',
        *(extra_args or []),
        '-R',
        *[str(p.expanduser()) for p in paths],
    ]
    logger.debug("Running command '{} {}'", ctags_executable, ' '.join(cmd_args))
    proc = await asyncio.subprocess.create_subprocess_exec(
        ctags_executable, *cmd_args,
    )
    await proc.communicate()
