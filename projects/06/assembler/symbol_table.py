

class SymbolTable(object):

    def __init__(self):
        self._table = {
            f'R{i}': i for i in range(16)
        }
        self._table['SP'] = 0
        self._table['LCL'] = 1
        self._table['ARG'] = 2
        self._table['THIS'] = 3
        self._table['THAT'] = 4
        self._table['SCREEN'] = 16384
        self._table['KBD'] = 24576

    def __getitem__(self, name):
        if name not in self._table:
            raise KeyError(f'{self} does not contains key {name}')
        return self._table[name]

    def __setitem__(self, name, value):
        self._table[name] = value

    def __contains__(self, name):
        return name in self._table
