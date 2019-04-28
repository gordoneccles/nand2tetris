from encoder import (
    ArithmeticEncoder, MemoryEncoder, FlowControlEncoder, FunctionEncoder,
    InitEncoder,
)
from glob import glob
import os
from parser import Parser


class Runner(object):

    def __init__(self, input_fname):
        self._in_fname = input_fname

    def run(self, out_f):
        if os.path.isdir(self._in_fname):
            files = glob(os.path.join(self._in_fname, '*.vm'))
        else:
            files = [self._in_fname]

        with open(out_f, 'w') as out_f:
            for asm_line in InitEncoder().encode():
                out_f.write('{}\n'.format(asm_line))

            for vm_file in files:
                self._translate_file(vm_file, out_f)

    def _translate_file(self, vm_filename, out_f):
        func_scope = None
        for tokens, instr_type in Parser.parse_lines(vm_filename):

            encoder = self._encoder_for(vm_filename, instr_type, func_scope)
            if (
                isinstance(encoder, FunctionEncoder) and
                encoder.is_func_declaration(tokens[0])
            ):
                func_scope = tokens[1]

            for idx, asm_line in enumerate(encoder.encode(*tokens)):
                if idx == 0:
                    comment = f'// {" ".join(tokens)}'
                    out_f.write('{} {}\n'.format(asm_line, comment))
                else:
                    out_f.write('{}\n'.format(asm_line))

    def _encoder_for(self, vm_filename, instr_type, func_scope):
        namespace = os.path.basename(vm_filename).rstrip('.vm')
        encoders = {
            Parser.C_ARITHMETIC: ArithmeticEncoder(),
            Parser.C_MEMORY: MemoryEncoder(namespace),
            Parser.C_FLOW_CONTROL: FlowControlEncoder(func_scope),
            Parser.C_FUNCTION: FunctionEncoder(namespace),
        }

        if instr_type not in encoders:
            raise ValueError(f'Unexpected instruction type {instr_type}')

        return encoders[instr_type]
