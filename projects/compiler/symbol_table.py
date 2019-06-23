from collections import namedtuple
from typing import Optional, Union


Symbol = namedtuple("Symbol", ["name", "kind", "typ", "index"])


class SymbolTable(object):

    STATIC = "STATIC"
    FIELD = "FIELD"
    ARG = "ARG"
    VAR = "VAR"

    def __init__(self):
        self._class_table = {}
        self._subroutine_table = None
        self._next_indices = {self.STATIC: 0, self.FIELD: 0}

    def start_subroutine(self, is_method: bool) -> None:
        self._subroutine_table = {}
        self._next_indices[self.ARG] = 1 if is_method else 0
        self._next_indices[self.VAR] = 0

    def complete_subroutine(self):
        self._subroutine_table = None
        del self._next_indices[self.ARG]
        del self._next_indices[self.VAR]

    def define(self, name: str, typ: str, kind: str) -> None:
        if kind not in self._next_indices:
            raise ValueError(f"Unknown kind of identifier {kind}")

        index = self._next_indices[kind]
        self._next_indices[kind] += 1

        if kind in [self.STATIC, self.FIELD]:
            self._class_table[name] = Symbol(name, kind, typ, index)
        else:
            self._subroutine_table[name] = Symbol(name, kind, typ, index)

    def var_count(self, kind: str) -> int:
        if kind not in self._next_indices:
            raise ValueError(f"Unknown kind of identifier {kind}")

        return self._next_indices[kind]

    def kind_of(self, name: str) -> Optional[str]:
        return self._get(name, "kind")

    def type_of(self, name: str) -> Optional[str]:
        return self._get(name, "typ")

    def index_of(self, name: str) -> Optional[int]:
        return self._get(name, "index")

    def has(self, name: str) -> bool:
        return name in self._subroutine_table or name in self._class_table

    def _get(self, name: str, attr: str) -> Union[str, int, None]:
        if name in self._subroutine_table:
            return getattr(self._subroutine_table[name], attr)
        elif name in self._class_table:
            return getattr(self._class_table[name], attr)
