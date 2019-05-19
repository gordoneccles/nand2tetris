from collections import namedtuple
import re


CLASS = 'class'
METHOD = 'method'
FUNCTION = 'function'
CONSTRUCTOR = 'constructor'
INT = 'int'
BOOLEAN = 'boolean'
CHAR = 'char'
VOID = 'void'
VAR = 'var'
STATIC = 'static'
FIELD = 'field'
LET = 'let'
DO = 'do'
IF = 'if'
ELSE = 'else'
WHILE = 'while'
RETURN  = 'return'
TRUE = 'true'
FALSE = 'false'
NULL = 'null'
THIS = 'this'
KEYWORDS = {
    CLASS,
    METHOD,
    FUNCTION,
    CONSTRUCTOR,
    INT,
    BOOLEAN,
    CHAR,
    VOID,
    VAR,
    STATIC,
    FIELD,
    LET,
    DO,
    IF,
    ELSE,
    WHILE,
    RETURN,
    TRUE,
    FALSE,
    NULL,
    THIS,
}
SYMBOLS = {
    '{', '}', '(', ')', '[', ']', '.', ',', ';',
    '+', '-', '*', '/', '&', '|', '<', '>', '=', '~',
}

SYMBOL = 'symbol'
KEYWORD = 'keyword'
STRING_VAL = 'string_val'
INT_VAL = 'int_val'
IDENTIFIER = 'identifier'


Token = namedtuple('Token', ['value', 'type'])


class TokenizerException(Exception):
    pass


class Tokenizer(object):

    def __init__(self, jack_fname):
        self._jack_fname = jack_fname
        self._stream = self._token_stream()
        self._tokens_so_far = []
        self._rewind_ct = 0

    def next_token(self):
        if self._rewind_ct > 0:
            self._rewind_ct -= 1
            return self._tokens_so_far[-(self._rewind_ct + 1)]

        try:
            token = next(self._stream)
            self._tokens_so_far.append(token)
            return token
        except StopIteration:
            return None

    def rewind(self):
        self._rewind_ct += 1

        if self._rewind_ct > len(self._tokens_so_far):
            raise TokenizerException('Cannot rewind any further.')

    def _token_stream(self):
        file_data = open(self._jack_fname, 'r').read()
        file_data = re.sub(r'//.*\n', '', file_data)
        file_data = re.sub(r'/\*\*.*\*/', '', file_data)
        course_tokens = re.split(r'\s+', file_data)

        token = ''
        for course_token in course_tokens:
            for char in course_token:
                if char in SYMBOLS:
                    if token:
                        yield Token(token, self._type_for(token))
                        token = ''
                    yield Token(char, SYMBOL)
                else:
                    token += char
            if token:
                yield Token(token, self._type_for(token))
                token = ''

    def _type_for(self, token):
        if token in KEYWORDS:
            return KEYWORD
        elif re.match(r'^"[^"]*"$', token):
            return STRING_VAL
        elif re.match(r'^[0-9]+$',  token):
            return INT_VAL
        elif re.match(r'[a-zA-Z_]+[a-zA-Z_0-9]*', token):
            return IDENTIFIER
        else:
            raise ValueError(f'Unable to identify token {token}')
