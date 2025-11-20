from pathlib import Path

from dataclasses import dataclass


@dataclass
class AddLine:
    content: str


class Editor:
    def __init__(self, path: Path):
        self.path = path

    def apply_new_lines(self, changes: list[AddLine]) -> None:
        with open(self.path, "r") as f:
            lines = f.readlines()

        # find a line that starts with "import" or "from"
        for insert_point, line in enumerate(lines):
            if line.startswith("import") or line.startswith("from"):
                break
        else:
            insert_point = 0

        for change in changes:
            lines.insert(insert_point, change.content + "\n")

        with open(self.path, "w") as f:
            f.writelines(lines)
