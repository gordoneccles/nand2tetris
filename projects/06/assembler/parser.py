import re


class ParsingException(Exception):
    pass


class Parser(object):
    A_INSTRUCTION = 'A_INSTRUCTION'
    C_INSTRUCTION = 'C_INSTRUCTION'
    LABEL_DECLARATION = 'LABEL_DECLARATION'

    @staticmethod
    def _validate_label(label):
        if not re.match(r'[a-zA-Z_\.\$:]+[a-zA-Z0-9_\.\$:]*', label):
            raise ParsingException(
                f'Label "{line}" includes invalid characters'
            )

    @staticmethod
    def _validate_a_val(a_val):
        if not re.match(r'[0-9]+', a_val) and not re.match(
            r'[a-zA-Z_\.\$:]+[a-zA-Z0-9_\.\$:]*', a_val
        ):
            raise ParsingException(
                f'A instruction value "{a_val}" includes invalid characters'
            )

    def _validate_c_instruction(line):
        if len(line.split(';')) > 2:
            raise ParsingException('Invalid instruction: "{line"}')
        elif len(line.split('=')) > 2:
            raise ParsingException('Invalid instruction: "{line"}')

    @classmethod
    def parse_lines(cls, fname):
        with open(fname, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('//'):
                    continue

                line = re.sub(r'\s*//.*$', '', line)

                if line.startswith('('):
                    label = line[1:-1]
                    cls._validate_label(label)
                    yield [label], cls.LABEL_DECLARATION
                elif line.startswith('@'):
                    a_val = line[1:]
                    cls._validate_a_val(a_val)
                    yield [a_val], cls.A_INSTRUCTION
                else:
                    cls._validate_c_instruction(line)
                    if '=' in line:
                        dest, line = line.split('=')
                    else:
                        dest = None

                    if ';' in line:
                        cmd, jmp = line.split(';')
                    else:
                        cmd, jmp = line, None

                    yield [dest, cmd, jmp], cls.C_INSTRUCTION
