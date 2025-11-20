from dataclasses import dataclass

from import_completer.completer import Completer


@dataclass
class C:
    a: int


completer = Completer()
print("test")
