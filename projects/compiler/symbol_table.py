from collections import namedtuple
from typing import Optional, Union


Identifier = namedtuple('Identifier', ['name', 'typ', 'index'])


class SymbolTable(object):

    STATIC = 'STATIC'
    FIELD = 'FIELD'
    ARG = 'ARG'
    VAR = 'VAR'

    def __init__(self):
        self._class_table = {}
        self._subroutine_table = None
        self._next_indices = {
            self.STATIC: 0,
            self.FIELD: 0,
            self.ARG: 0,
            self.VAR: 0,
        }

    def start_subroutine(self): -> None
        self._subroutine_table = {}
        self._next_index[self.ARG] = 0
        self._next_index[self.VAR] = 0

    def define(self, name: str, typ: str, kind: str): -> None
        if kind not in self._next_indices:
            raise ValueError(f'Unknown kind of identifier {kind}')

        index = self._next_index[kind]
        self._next_index[kind] += 1

        if kind in [self.STATIC, self.FIELD]:
            self._class_table[name] = Identifier(name, typ, index)
        else:
            self._subroutine_table[name] = Identifier(name, typ, index)

    def var_count(self, kind): -> int
        if kind not in self._next_indices:
            raise ValueError(f'Unknown kind of identifier {kind}')

        return self._next_index[kind]

    def kind_of(self, name): -> Optional[str]
        return self._get(name 'kind')

    def type_of(self, name): -> Optional[str]
        return self._get(name 'typ')

    def index_of(self, name): -> Optional[int]
        return self._get(name 'index')

    def _get(self, name: str, attr: str): -> Union[str, int, None]
        if name in self._subroutine_table:
            return getattr(self._subroutine_table[name], attr)
        elif name in self._class_table:
            return getattr(self._subroutine_table[name], attr)
