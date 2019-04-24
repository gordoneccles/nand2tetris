from abc import ABC, abstractmethod
from uuid import uuid4


class EncodingException(Exception):
    pass


class AbstractEncoder(ABC):

    @abstractmethod
    def encode(self, *args, **kwargs):
        raise NotImplementedError()


_jmp_label_ct = 0


class ArithmeticEncoder(AbstractEncoder):
    _LOAD_UNARY = [
        '@SP', 'D=M-1', 'M=D', 'A=D', 'D=M',
    ]
    _LOAD_BINARY = [
        '@SP', 'D=M-1', 'D=D-1', 'M=D', 'A=D+1', 'D=M', 'A=A-1',
    ]
    _STORE = [
        '@SP', 'A=M', 'M=D', 'D=A+1', '@SP', 'M=D',
    ]

    def _encode_math_or_logic(self, cmd):
        if cmd in ['add', 'sub', 'and', 'or']:
            load_lines = self._LOAD_BINARY[:]
        else:
            load_lines = self._LOAD_UNARY[:]

        asm_cmd = {
            'add': 'D=D+M',
            'sub': 'D=M-D',
            'neg': 'D=-D',
            'and': 'D=D&M',
            'or': 'D=D|M',
            'not': 'D=!D',
        }[cmd]

        return load_lines + [asm_cmd] + self._STORE

    def _encode_comp(self, cmd):
        global _jmp_label_ct
        true_label = f'JMP_{cmd}_{_jmp_label_ct}'.upper()
        end_label = f'END_JMP_{cmd}_{_jmp_label_ct}'.upper()
        _jmp_label_ct += 1

        if cmd == 'gt':
            jmp_cmd = 'D;JGT'
        elif cmd == 'lt':
            jmp_cmd = 'D;JLT'
        else:
            jmp_cmd = 'D;JEQ'

        comp_lines = [
            'D=M-D',
            f'@{true_label}',
            jmp_cmd,
            'D=0',
            f'@{end_label}',
            '0;JMP',
            f'({true_label})',
            'D=-1',
            f'({end_label})',
        ]

        return self._LOAD_BINARY[:] + comp_lines + self._STORE

    def encode(self, cmd):
        if cmd in ['add', 'sub', 'neg', 'and', 'or', 'not']:
            return self._encode_math_or_logic(cmd)
        elif cmd in ['gt', 'lt', 'eq']:
            return self._encode_comp(cmd)
        else:
            raise EncodingException(f'Unknown arithemtic command "{cmd}".')


class MemoryEncoder(AbstractEncoder):

    PUSH = 'push'
    POP = 'pop'

    ARGUMENT = 'argument'
    LOCAL = 'local'
    THIS = 'this'
    THAT = 'that'
    POINTER = 'pointer'
    STATIC = 'static'
    CONSTANT = 'constant'
    TEMP = 'temp'
    POINTER_SEGMENTS_MAP = {
        ARGUMENT: 'ARG',
        LOCAL: 'LCL',
        THIS: 'THIS',
        THAT: 'THAT',
    }

    @staticmethod
    def _do_push():
        return [
           '@SP',
           'A=M',
           'M=D',
           'D=A+1',
           '@SP',
           'M=D',
        ]

    @staticmethod
    def _prep_for_pop():
        return [
           '@SP',
           'D=M-1',
           'M=D',
           'A=D',
           'D=M',
        ]

    def __init__(self, static_prefix):
        self._static_prefix = static_prefix

    def encode(self, cmd, seg_name, value):
        if cmd not in [self.PUSH, self.POP]:
            raise EncodingException(f'Unknown stack command "{cmd}"')

        try:
            value = int(value)
        except:
            raise EncodingException('Value must be an integer.')

        if seg_name == self.CONSTANT:
            if cmd != self.PUSH:
                raise EncodingException(
                    f'Cannot apply "{cmd}" to constant segment.'
                )
            return self._encode_constant_seg(value)
        elif seg_name in self.POINTER_SEGMENTS_MAP:
            return self._encode_pointer_segs(cmd, seg_name, value)
        elif seg_name in [self.TEMP, self.POINTER]:
            return self._encode_fixed_segs(cmd, seg_name, value)
        elif seg_name == self.STATIC:
            return self._encode_static_seg(cmd, value)
        else:
            raise EncodingException(f'Unknown memory segment "{seg_name}".')

    def _encode_constant_seg(self, value):
        return [
            f'@{value}',
            'D=A',
        ] + self._do_push()

    def _encode_pointer_segs(self, cmd, seg_name, index):
        reg = self.POINTER_SEGMENTS_MAP[seg_name]
        if cmd == self.PUSH:
            lines = [f'@{reg}', 'A=M']
            for _ in range(index):
                lines.append('A=A+1')
            lines.append('D=M')
            lines.extend(self._do_push())
        else:
            lines = self._prep_for_pop()
            lines.extend([
                f'@{reg}',
                'A=M',
            ])
            lines.extend(['A=A+1'] * index)
            lines.append('M=D')

        return lines

    def _encode_fixed_segs(self, cmd, seg_name, index):
        if seg_name == self.POINTER:
            if index > 1:
                raise EncodingException('Cannot index pointer segment above 1.')
            base = 3
        elif seg_name == self.TEMP:
            if index > 7:
                raise EncodingException('Cannot index temp segment above 7.')
            base = 5
        else:
            raise ValueError(f'Bad segment "{seg_name}" for fixed encoding.')

        if cmd == self.PUSH:
            lines = [f'@R{index + base}', 'D=M']
            lines.extend(self._do_push())
        else:
            lines = self._prep_for_pop()
            lines.extend([
                f'@R{index + base}',
                'M=D',
            ])

        return lines

    def _encode_static_seg(self, cmd, index):
        var_name = '.'.join([self._static_prefix, str(index)])

        if cmd == self.PUSH:
            lines = [f'@{var_name}', 'D=M']
            lines.extend(self._do_push())
        else:
            lines = self._prep_for_pop()
            lines.extend([
                f'@{var_name}',
                'M=D',
            ])

        return lines
