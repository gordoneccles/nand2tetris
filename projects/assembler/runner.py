import re

from parser import Parser
from encoder import Encoder
from symbol_table import SymbolTable


class Runner(object):
    @staticmethod
    def _is_symbol(val):
        return bool(re.match(r"[a-zA-Z_\.\$:]+[a-zA-Z0-9_\.\$:]*", val))

    def __init__(self, input_fname):
        self._in_fname = input_fname

    def run(self, out_fname):
        sym_tab = self._build_symbol_table()
        self._write(out_fname, sym_tab)

    def _build_symbol_table(self):
        sym_tab = SymbolTable()
        line_no = 0
        for tokens, instr_type in Parser.parse_lines(self._in_fname):
            if instr_type == Parser.LABEL_DECLARATION:
                if self._is_symbol(tokens[0]):
                    sym_tab[tokens[0]] = line_no
                continue

            line_no += 1

        mem_addr = 16
        for tokens, instr_type in Parser.parse_lines(self._in_fname):
            if (
                instr_type == Parser.A_INSTRUCTION
                and self._is_symbol(tokens[0])
                and tokens[0] not in sym_tab
            ):
                sym_tab[tokens[0]] = mem_addr
                mem_addr += 1

        return sym_tab

    def _write(self, out_fname, sym_tab):
        with open(out_fname, "w") as out_f:
            for tokens, instr_type in Parser.parse_lines(self._in_fname):
                if instr_type == Parser.A_INSTRUCTION:
                    if self._is_symbol(tokens[0]):
                        val = Encoder.encode_a(sym_tab[tokens[0]])
                    else:
                        val = Encoder.encode_a(tokens[0])
                elif instr_type == Parser.C_INSTRUCTION:
                    val = Encoder.encode_c(tokens[0], tokens[1], tokens[2])
                elif instr_type == Parser.LABEL_DECLARATION:
                    continue
                else:
                    raise ValueError(
                        f"Unexpected instruction type {instr_type}"
                    )

                out_f.write("{}\n".format(val))
