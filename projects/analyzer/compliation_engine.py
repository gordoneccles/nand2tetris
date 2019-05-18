from tokenizer import (
    Tokenizer, SYMBOL, KEYWORD, STRING_VAL, INT_VAL, IDENTIFIER
)


class CompilationException(Exception):
    pass


_indent = 0


def _o_tag(s):
    return f'<{s}>\n'


def _c_tag(s):
    return f'</{s}>\n'


def _tagged(tag_name, s):
    return f'<{tag_name}>{s}</{tag_name}\n'


def _new_xml_section(section_name):

    def _outer(fn):

        def _inner(*args, **kwargs):
            f = args[1]
            f.write(_o_tag(section_name))
            global _indent
            _indent += 1
            ret = fn(*args, **kwargs)
            f.write(_c_tag(section_name))
            _indent -= 1
            return ret

        return _inner

    return _outer


def _write(token, expect, f, tag):
    if isinstance(expect, list):
        if token.value not in expect:
            raise CompilationException(
                f'Expected "{expect}", found "{token.value}".
            )

    if token.value != expect:
        raise CompilationException(
            f'Expected "{expect}", found "{token.value}".
        )

    f.write(_tagged(tag, token.value))


def _write_keyword(token, expect, f):
    return  _write_keyword(token, expect, f)


def _write_symbol(token, expect, f):
    return  _write_symbol(token, expect, f)


def _write_identifier(token, f):
    if token.type != IDENTIFIER:
        raise CompilationException(
            f'Expected instance of {expect_type}, '
            'found {actual_type} "{token.type}"'
        )
    f.write(_tagged(IDENTIFIER, token.value))


def _write_type(token, f, include_void=False):
    type_keywords = ['int', 'char', 'boolean']
    if include_void:
        type_keywords.append('void')

    if token.type == KEYWORD:
        _write_keyword(token, type_keywords, f)
    else:
        _write_identifier(token, f)


class CompilationEngine(object):

    def __init__(self, jack_fname):
        self._jack_fname = jack_fname

    def compile(self, out_fname):
        tokenizer = Tokenizer(jack_fname)
        with open(out_fname) as f:
            self._compile(f, tokenizer)

    _new_xml_section('tokens')
    def _compile(self, f, tokenizer):
        token = tokenizer.next_token()
        nxt_token = self._compile_class(f, tokenizer, token)
        if next_token:
            raise CompilationException(
                f'Expected end of file, found {next_token}'
            )

    _new_xml_section('class')
    def _compile_class(self, f, tokenizer, token):
        _write_keyword(token, 'class', f)
        _write_identifier(tokenizer.next_token(), f)
        _write_symbol(tokenizer.next_token(), '{', f)

        token = tokenizer.next_token()
        while token.value in ['static', 'field']:
            token = self._compile_class_var_dec(f, tokenizer, token)

        while token.value in ['constructor', 'function', 'method']:
            token = self._compile_subroutine_dec(f, tokenizer, token)

        _write_symbol(token, '}', f)
        return tokenizer.next_token()

    _new_xml_section('classVarDec')
    def _compile_class_var_dec(self, f, tokenizer, token):
        _write_keyword(token, ['static', 'field'], f)
        _write_type(tokenizer.next_token(), f)
        _write_identifier(tokenizer.next_token(), f)

        token = tokenizer.next_token()
        while token.value == ',':
            _write_symbol(token, ',', f)
            _write_identifier(tokenizer.next_token(), f)
            token = tokenizer.next_token()

        _write_symbol(token, ';', f)
        return tokenizer.next_token()

    _new_xml_section('subroutineDec')
    def _compile_subroutine_dec(self, f, tokenizer, token):
        _write_keyword(token, ['constructor', 'function', 'method'], f)
        _write_type(tokenizer.next_token(), f, include_void=True)
        _write_identifier(tokenizer.next_token(), f)
        _write_symbol(tokenizer.next_token(), '(', f)

        token = self._compile_parameter_list(f, tokenizer, token)
        _write_symbol(token, ')', f)

        token = self._compile_subroutine_body(f, tokenizer, token)
        return tokenizer.next_token()

    _new_xml_section('parameterList')
    def _compile_parameter_list(self, f, tokenizer, token):
        if not (
            token.value in ['int', 'char', 'boolean']
            or token.type == IDENTIFIER
        ):
            return token

        while True:
            _write_type(token, f)
            _write_identifier(tokenizer.next_token(), f)

            token = tokenizer.next_token()
            if token.value == ',':
                _write_symbol(token, ',', f)
                token = tokenizer.next_token()
            else:
                return token

    _new_xml_section('subroutineBody')
    def _compile_subroutine_body(self, f, tokenizer, token):
        _write_symbol(token, '{', f)

        token = tokenizer.next_token()
        if token.value == 'var':
            token = self._compile_var_dec(f, tokenizer, token)

        token = self._compile_statements(f, tokenizer, token)
        _write_symbol(token, '}', f)

        return tokenizer.next_token()

    _new_xml_section('varDec')
    def _compile_var_dec(self, f, tokenizer, token):
        _write_keyword(token, 'var', f)

        while True:
            _write_type(tokenizer.next_token(), f)
            _write_identifier(tokenizer.next_token(), f)

            token = tokenizer.next_token()
            if token.value == ',':
                _write_symbol(token, ',', f)
            else:
                _write_symbol(token, ';', f)
                return tokenizer.next_token()

    _new_xml_section('statements')
    def _compile_statements(self, f, tokenizer, token):
        while token.value in ['let', 'if', 'while', 'do', 'return']:
            method = getattr(self, f'_compile_{token.value}')
            token = method(f, tokenizer, token)

        return token

    _new_xml_section('letStatement')
    def _compile_let(self, f, tokenizer, token):
        _write_keyword(token, 'let', f)
        _write_identifier(tokenizer.next_token(), f)

        if token.value == '[':
            _write_symbol(token, '[', f)
            token = self._compile_expression(
                f, tokenizer, tokenizer.next_token()
            )
            _write_symbol(token, ']', f)
            token = tokenizer.next_token()

        _write_symbol(token, '=', f)
        token = self._compile_expression(f, tokenizer, tokenizer.next_token())

        _write_symbol(token, ';', f)
        return tokenizer.next_token()

    _new_xml_section('ifStatement')
    def _compile_if(self, f, tokenizer, token):
        _write_keyword(token, 'if', f)
        _write_symbol(tokenizer.next_token(), '(', f)

        token = self._compile_expression(f, tokenizer, tokenizer.next_token())
        _write_symbol(token, ')', f)
        _write_symbol(tokenizer.next_token(), '{', f)

        token = self._compile_statements(f, tokenizer, tokenizer.next_token())
        _write_symbol(token, '}', f)

        token = tokenizer.next_token()
        if token.value == 'else':
            _write_keyword(token, 'else', f)

            _write_symbol(tokenizer.next_token(), '{', f)

            token = self._compile_statements(
                f, tokenizer, tokenizer.next_token()
            )
            _write_symbol(token, '}', f)

        return token

    _new_xml_section('whileStatement')
    def _compile_while(self, f, tokenizer, token):
        _write_keyword(token, 'while', f)
        _write_symbol(tokenizer.next_token(), '(', f)

        token = self._compile_expression(f, tokenizer, tokenizer.next_token())
        _write_symbol(token, ')', f)
        _write_symbol(tokenizer.next_token(), '{', f)

        token = self._compile_statements(f, tokenizer, tokenizer.next_token())
        _write_symbol(token, '}', f)
        return tokenizer.next_token()

    _new_xml_section('doStatement')
    def _compile_do(self, f, tokenizer, token):
        _write_keyword(token, 'do', f)

        token = self._compile_subroutine_call(
            f, tokenizer, tokenizer.next_token()
        )
        _write_symbol(tokenizer.next_token(), ';', f)
        return tokenizer.next_token()

    _new_xml_section('returnStatement')
    def _compile_return(self, f, tokenizer, token):
        _write_keyword(token, 'return', f)
        token = tokenizer.next_token()
        if token.value != ';':
            token = self._compile_expression(f, tokenizer, token)

        _write_symbol(token, ';', f)
        return tokenizer.next_token()
