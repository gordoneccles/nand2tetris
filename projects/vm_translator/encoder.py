from abc import ABC, abstractmethod


PUSH = "push"
POP = "pop"

ADD = "add"
SUB = "sub"
NEG = "neg"
AND = "and"
OR = "or"
NOT = "not"

GT = "gt"
LT = "lt"
EQ = "eq"

LCL = "LCL"
ARG = "ARG"
THIS = "THIS"
THAT = "THAT"

SEG_STATIC = "static"
SEG_THIS = "this"
SEG_ARGUMENT = "argument"
SEG_LOCAL = "local"

SEG_THAT = "that"
SEG_POINTER = "pointer"
SEG_CONSTANT = "constant"
SEG_TEMP = "temp"

_LOAD_UNARY = ["@SP", "D=M-1", "M=D", "A=D", "D=M"]
_jmp_label_ct = 0
_call_label_ct = 0


def _do_push():
    return ["@SP", "A=M", "M=D", "D=A+1", "@SP", "M=D"]


class EncodingException(Exception):
    pass


class AbstractEncoder(ABC):
    @abstractmethod
    def encode(self, *args, **kwargs):
        raise NotImplementedError()


class ArithmeticEncoder(AbstractEncoder):
    _LOAD_BINARY = ["@SP", "D=M-1", "D=D-1", "M=D", "A=D+1", "D=M", "A=A-1"]
    _STORE = ["@SP", "A=M", "M=D", "D=A+1", "@SP", "M=D"]

    def _encode_math_or_logic(self, cmd):
        if cmd in [ADD, SUB, AND, OR]:
            load_lines = self._LOAD_BINARY[:]
        else:
            load_lines = _LOAD_UNARY[:]

        asm_cmd = {
            ADD: "D=D+M",
            SUB: "D=M-D",
            NEG: "D=-D",
            AND: "D=D&M",
            OR: "D=D|M",
            NOT: "D=!D",
        }[cmd]

        return load_lines + [asm_cmd] + self._STORE

    def _encode_comp(self, cmd):
        global _jmp_label_ct
        true_label = f"JMP_{cmd}_{_jmp_label_ct}".upper()
        end_label = f"END_JMP_{cmd}_{_jmp_label_ct}".upper()
        _jmp_label_ct += 1

        if cmd == GT:
            jmp_cmd = "D;JGT"
        elif cmd == LT:
            jmp_cmd = "D;JLT"
        else:
            jmp_cmd = "D;JEQ"

        comp_lines = [
            "D=M-D",
            f"@{true_label}",
            jmp_cmd,
            "D=0",
            f"@{end_label}",
            "0;JMP",
            f"({true_label})",
            "D=-1",
            f"({end_label})",
        ]

        return self._LOAD_BINARY[:] + comp_lines + self._STORE

    def encode(self, cmd):
        if cmd in [ADD, SUB, NEG, AND, OR, NOT]:
            return self._encode_math_or_logic(cmd)
        elif cmd in [GT, LT, EQ]:
            return self._encode_comp(cmd)
        else:
            raise EncodingException(f'Unknown arithemtic command "{cmd}".')


class MemoryEncoder(AbstractEncoder):

    POINTER_SEGMENTS_MAP = {
        SEG_ARGUMENT: ARG,
        SEG_LOCAL: LCL,
        SEG_THIS: THIS,
        SEG_THAT: THAT,
    }

    @staticmethod
    def _prep_for_pop():
        return ["@SP", "D=M-1", "M=D", "A=D", "D=M"]

    def __init__(self, class_scope):
        self._class_scope = class_scope

    def encode(self, cmd, seg_name, value):
        if cmd not in [PUSH, POP]:
            raise EncodingException(f'Unknown stack command "{cmd}"')

        try:
            value = int(value)
        except:
            raise EncodingException("Value must be an integer.")

        if seg_name == SEG_CONSTANT:
            if cmd != PUSH:
                raise EncodingException(
                    f'Cannot apply "{cmd}" to constant segment.'
                )
            return self._encode_constant_seg(value)
        elif seg_name in self.POINTER_SEGMENTS_MAP:
            return self._encode_pointer_segs(cmd, seg_name, value)
        elif seg_name in [SEG_TEMP, SEG_POINTER]:
            return self._encode_fixed_segs(cmd, seg_name, value)
        elif seg_name == SEG_STATIC:
            return self._encode_static_seg(cmd, value)
        else:
            raise EncodingException(f'Unknown memory segment "{seg_name}".')

    def _encode_constant_seg(self, value):
        return [f"@{value}", "D=A"] + _do_push()

    def _encode_pointer_segs(self, cmd, seg_name, index):
        reg = self.POINTER_SEGMENTS_MAP[seg_name]
        if cmd == PUSH:
            lines = [f"@{reg}", "A=M"]
            for _ in range(index):
                lines.append("A=A+1")
            lines.append("D=M")
            lines.extend(_do_push())
        else:
            lines = self._prep_for_pop()
            lines.extend([f"@{reg}", "A=M"])
            lines.extend(["A=A+1"] * index)
            lines.append("M=D")

        return lines

    def _encode_fixed_segs(self, cmd, seg_name, index):
        if seg_name == SEG_POINTER:
            if index > 1:
                raise EncodingException("Cannot index pointer segment above 1.")
            base = 3
        elif seg_name == SEG_TEMP:
            if index > 7:
                raise EncodingException("Cannot index temp segment above 7.")
            base = 5
        else:
            raise ValueError(f'Bad segment "{seg_name}" for fixed encoding.')

        if cmd == PUSH:
            lines = [f"@R{index + base}", "D=M"]
            lines.extend(_do_push())
        else:
            lines = self._prep_for_pop()
            lines.extend([f"@R{index + base}", "M=D"])

        return lines

    def _encode_static_seg(self, cmd, index):
        var_name = ".".join([self._class_scope, str(index)])

        if cmd == PUSH:
            lines = [f"@{var_name}", "D=M"]
            lines.extend(_do_push())
        else:
            lines = self._prep_for_pop()
            lines.extend([f"@{var_name}", "M=D"])

        return lines


class FlowControlEncoder(AbstractEncoder):
    def __init__(self, func_scope):
        self._func_scope = func_scope

    def encode(self, cmd, arg):
        if cmd == "goto":
            return self._encode_goto(arg, False)
        elif cmd == "if-goto":
            return self._encode_goto(arg, True)
        else:
            return self._encode_label(arg)

    def _scoped_label_for(self, label_name):
        label_parts = []
        if self._func_scope is not None:
            label_parts.append(self._func_scope)
        label_parts.append(label_name)
        return "$".join(label_parts)

    def _encode_goto(self, jmp_label, is_conditional):
        scoped_label = self._scoped_label_for(jmp_label)
        if is_conditional:
            lines = _LOAD_UNARY[:]
            lines.extend([f"@{scoped_label}", "D;JLT", "D;JGT"])
            return lines
        else:
            return [f"@{scoped_label}", "0;JMP"]

    def _encode_label(self, label_name):
        scoped_label = self._scoped_label_for(label_name)
        return [f"({scoped_label})"]


class FunctionEncoder(AbstractEncoder):

    SAVED_CALLER_STATE = [LCL, ARG, THIS, THAT]
    NUM_SAVED_VARS = len(SAVED_CALLER_STATE) + 1  # 1 extra for return address

    @staticmethod
    def is_func_declaration(cmd):
        return cmd == "function"

    @staticmethod
    def is_func_return(cmd):
        return cmd == "return"

    def __init__(self, class_scope):
        self._class_scope = class_scope

    def encode(self, cmd, *args):
        if self.is_func_declaration(cmd):
            if len(args) != 2:
                raise EncodingException(
                    '"function" command requires two arguments: function name'
                    " and num local variables. Received: {}".format(args)
                )
            return self._encode_func_declaration(args[0], args[1])
        elif self.is_func_return(cmd):
            if len(args) != 0:
                raise EncodingException(
                    '"return" command takes no arguments.'
                    " Received {}".format(args)
                )
            return self._encode_func_return()
        else:
            if len(args) != 2:
                raise EncodingException(
                    '"call" command requires two arguments: function name'
                    " and num local variables. Received: {}".format(args)
                )
            return self._encode_call(args[0], args[1])

    def _encode_func_declaration(self, func_name, n_vars):
        lines = [f"({func_name})"]
        for idx in range(int(n_vars)):
            m_enc = MemoryEncoder(self._class_scope)
            lines.extend(m_enc.encode(PUSH, SEG_CONSTANT, "0"))
        return lines

    def _encode_call(self, func_name, n_vars):
        global _call_label_ct
        lines = []
        return_label = f"RETURN_FROM_{func_name}_{_call_label_ct}"
        _call_label_ct += 1

        lines.extend(
            [f"@{return_label}", "D=A"]
        )  # push return address onto stack
        lines.extend(_do_push())

        for ptr_addr in self.SAVED_CALLER_STATE:
            lines.extend([f"@{ptr_addr}", "D=M"])
            lines.extend(_do_push())  # push func state onto stack

        # we rely on the fact that _do_push leaves SP in the A register
        lines.append("D=M")
        for _ in range(self.NUM_SAVED_VARS + int(n_vars)):
            lines.append("D=D-1")
        lines.extend(
            [
                f"@{ARG}",
                "M=D",  # reposition ARG to SP - n_vars - self.NUM_SAVED_VARS
                "@SP",
                "D=M",
                f"@{LCL}",
                "M=D",  # reposition LCL to SP
                f"@{func_name}",
                "0;JMP",  # jump to function
                f"({return_label})",
            ]
        )
        return lines

    def _encode_func_return(self):
        frame = "R13"
        ret = "R14"
        lines = ["@LCL", "D=M", f"@{frame}", "M=D", "A=D"]  # store LCL in frame
        for _ in range(self.NUM_SAVED_VARS):
            lines.append("A=A-1")
        lines.extend(
            [
                "D=M",
                f"@{ret}",
                "M=D",  # store return address in ret
                "@SP",
                "A=M-1",
                "D=M",
                f"@{ARG}",
                "A=M",
                "M=D",  # store the func's returned value in ARG
                "D=A+1",
                "@SP",
                "M=D",  # reset SP to ARG+1
            ]
        )

        for i, state in enumerate(reversed(self.SAVED_CALLER_STATE)):
            lines.extend([f"@{frame}", "A=M-1"])
            for j in range(i):
                lines.append("A=A-1")
            lines.extend(["D=M", f"@{state}", "M=D"])  # restore state of caller

        lines.extend([f"@{ret}", "A=M", "0;JMP"])  # go to return address

        return lines


class InitEncoder(AbstractEncoder):
    def encode(self):
        lines = ["@256", "D=A", "@SP", "M=D"]  # initialize SP to 256
        f_enc = FunctionEncoder("Sys")
        lines.extend(f_enc.encode("call", "Sys.init", "0"))
        return lines
