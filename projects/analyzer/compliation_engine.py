
from tokenizer import (
    Tokenizer, SYMBOL, KEYWORD, STRING_VAL, INT_VAL, IDENTIFIER
)


class CompilationEngine(object):

    @staticmethod
    def _o_tag(s):
        return f'<{s}>'

    @staticmethod
    def _c_tag(s):
        return f'</{s}>'

    def __init__(self, jack_fname):
        self._jack_fname = jack_fname
        self._indent = 0

    def compile(self, out_fname):
        tokenizer = Tokenizer(jack_fname)

        with open(out_fname) as f:
            f.write(self._o_tag('tokens'))
            self._updent()
            token, token_type = tokenizer.next_token_and_type()
            self._compile_class(f, tokenizer, token, token_type)
            self._dedent()
            f.write(self._c_tag('tokens'))

    def _updent(self):
        self._indent += 1

    def _dedent(self):
        self._indent -= 1

    def _tagged(tag_name, s):
        return f'<{tag_name}>{s}</{tag_name}\n'

    def _assert_equal(actual, expect):
        if isinstance(expect, list):
            if actual not in expect:
                raise ValueError(f'Expected "{expect}", found "{actual}".)

        if actual != expect:
            raise ValueError(f'Expected "{expect}", found "{actual}".)

    def _assert_type(actual_type, expect_type, token):
        if expect_type != actual_type:
            raise ValueError(
                f'Expected instance of {expect_type}, '
                'found {actual_type} "{token}"'
            )

    def _compile_class(self, f, tokenizer, token, token_type):
        f.write(self._o_tag('class') + '\n')
        self._updent()

        self._assert_equal(token, 'class')
        f.write(self._tagged(KEYWORD, token))

        token, token_type = tokenizer.next_token_and_type()
        self._assert_type(token_type, IDENTIFIER, token)
        f.write(self._tagged(IDENTIFIER, token))

        token, token_type = tokenizer.next_token_and_type()
        self._assert_equal(token, '{')
        f.write(self._tagged(SYMBOL, token))

        token, token_type = tokenizer.next_token_and_type()
        if token in ['static', 'field']:
            self._compile_class_var_dec(f, tokenizer, token, token_type):
            token, token_type = tokenizer.next_token_and_type()

        if token in ['constructor', 'function', 'method']:
            self._compile_subroutine_dec(f, tokenizer, token, token_type):
            token, token_type = tokenizer.next_token_and_type()

        self._assert_equal(token, '}')
        f.write(self._tagged(SYMBOL, token))

        self._dedent()
        f.write(self._c_tag('class') + '\n')

    def _compile_class_var_dec(self, f, tokenizer, token, token_type):
        f.write(self._o_tag('classVarDec') + '\n')
        self._updent()

        self._assert_equal(['static', 'field'], token)
        f.write(self._tagged(KEYWORD, token))

        token, token_type = tokenizer.next_token_and_type()
        if token_type == KEYWORD:
            self._assert_equal(['int', 'char', 'boolean'], token)
            f.write(self._tagged(KEYWORD, token))
        else:
            self._assert_type(token_type, IDENTIFIER, token)
            f.write(self._tagged(IDENTIFIER, token))

        token, token_type = tokenizer.next_token_and_type()
        self._assert_type(token_type, IDENTIFIER, token)
        f.write(self._tagged(IDENTIFIER, token))

        token, token_type = tokenizer.next_token_and_type()
        while token == ',':
            f.write(self._tagged(SYMBOL, token))
            token, token_type = tokenizer.next_token_and_type()
            self._assert_type(token_type, IDENTIFIER, token)
            f.write(self._tagged(IDENTIFIER, token))
            token, token_type = tokenizer.next_token_and_type()

        self._assert_equal(token, ';')
        f.write(self._tagged(SYMBOL, token))

        self._dedent()
        f.write(self._c_tag('classVarDec') + '\n')

    def _compile_subroutine_dec(self, f, toknizer, token, token_type):
        pass
