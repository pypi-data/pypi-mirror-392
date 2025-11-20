import subprocess
import sys
from collections.abc import Iterable
from pathlib import Path


def discover_paths_for_python_executable(
    python_executable: str = "python",
) -> Iterable[Path]:
    output = subprocess.check_output(
        [python_executable, "-c", r"import sys; print('\n'.join(sys.path))"]
    )
    for output_line in output.decode().splitlines():
        path = Path(output_line).absolute()
        if path.is_dir():
            yield path


def get_internal_python_paths() -> Iterable[Path]:
    return (Path(p) for p in sys.path)


if __name__ == "__main__":
    import sys

    python_executable = sys.argv[1] if len(sys.argv) > 1 else sys.executable
    for path in discover_paths_for_python_executable(python_executable):
        print(path)
