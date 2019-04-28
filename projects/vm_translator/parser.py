import re


class ParsingException(Exception):
    pass


class Parser(object):

    C_ARITHMETIC = 'C_ARITHMETIC'
    C_MEMORY = 'C_MEMORY'
    C_FLOW_CONTROL = 'C_FLOW_CONTROL'
    C_FUNCTION = 'C_FUNCTION'

    ARITHMETIC_CMDS = [
        'add',
        'sub',
        'neg',
        'eq',
        'gt',
        'lt',
        'and',
        'or',
        'not',
    ]
    MEMORY_CMDS = [
        'push',
        'pop',
    ]
    FLOW_CONTROL_CMDS = [
        'label',
        'goto',
        'if-goto',
    ]
    FUNCTION_CMDS = [
        'function',
        'call',
        'return',
    ]

    @staticmethod
    def _parse_line(line):
        line = line.strip()
        if not line or line.startswith('//'):
            return

        line = re.sub(r'\s*//.*$', '', line)
        return re.split(r'\s+', line)

    @staticmethod
    def _assert_num_args(n_args, args, cmd):
        if len(args) < n_args:
            raise ParsingException(
                f'Too few arguments for command "{cmd}". Expected {n_args}, '
                f'found {len(args)}: {", ".join(args)}.'
            )
        if len(args) > n_args:
            raise ParsingException(
                f'Too many arguments for command "{cmd}". Expected {n_args}, '
                f'found {len(args)}: {", ".join(args)}.'
            )

    @classmethod
    def parse_lines(cls, fname):
        with open(fname, 'r') as f:
            for line in f:
                tokens = cls._parse_line(line)
                if not tokens:
                    continue

                cmd = tokens[0]
                if cmd in cls.ARITHMETIC_CMDS:
                    cls._assert_num_args(0, tokens[1:], cmd)
                    yield tokens, cls.C_ARITHMETIC
                elif cmd in cls.MEMORY_CMDS:
                    cls._assert_num_args(2, tokens[1:], cmd)
                    yield tokens, cls.C_MEMORY
                elif cmd in cls.FLOW_CONTROL_CMDS:
                    cls._assert_num_args(1, tokens[1:], cmd)
                    yield tokens, cls.C_FLOW_CONTROL
                elif cmd in cls.FUNCTION_CMDS:
                    if cmd == 'return':
                        cls._assert_num_args(0, tokens[1:], cmd)
                    else:
                        cls._assert_num_args(2, tokens[1:], cmd)
                    yield tokens, cls.C_FUNCTION
                else:
                    raise ParsingException(f'Unknown command "{cmd}"')
