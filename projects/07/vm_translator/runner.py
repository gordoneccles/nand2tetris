from encoder import ArithmeticEncoder, MemoryEncoder
from parser import Parser


class Runner(object):

    def __init__(self, input_fname):
        self._in_fname = input_fname

    def run(self, out_f):
        with open(out_f, 'w') as out_f:
            for tokens, instr_type in Parser.parse_lines(self._in_fname):
                encoder = self._encoder_for(instr_type)
                out_f.write(f'// {" ".join(tokens)}\n')
                for asm_line in encoder.encode(*tokens):
                    out_f.write('{}\n'.format(asm_line))

    def _encoder_for(self, instr_type):
        static_prefix = self._in_fname.rstrip('.vm')
        encoders = {
            Parser.C_ARITHMETIC: ArithmeticEncoder(),
            Parser.C_MEMORY: MemoryEncoder(static_prefix),
            # Parser.C_FLOW_CONTROL: FlowControlEncoder,
            # Parser.C_FUNCTION: FunctionEncoder,
        }

        if instr_type not in encoders:
            raise ValueError(f'Unexpected instruction type {instr_type}')

        return encoders[instr_type]
