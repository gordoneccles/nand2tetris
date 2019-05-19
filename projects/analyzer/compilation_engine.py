from tokenizer import (
    Tokenizer, SYMBOL, KEYWORD, STRING_VAL, INT_VAL, IDENTIFIER,
    TRUE, FALSE, NULL, THIS,
)


class CompilationException(Exception):
    pass



def _o_tag(s):
    return f'<{s}>'


def _c_tag(s):
    return f'</{s}>'


def _tagged(tag_name, s):
    return f'{_o_tag(tag_name)}{s}{_c_tag(tag_name)}\n'


def _write(token, expect, f, tag):
    if isinstance(expect, list):
        if token.value not in expect:
            f.seek(0)
            print(f.read())
            raise CompilationException(
                f'Expected "{expect}", found "{token.value}".'
            )
    elif token.value != expect:
        f.seek(0)
        print(f.read())
        raise CompilationException(
            f'Expected "{expect}", found "{token.value}".'
        )

    f.write(_tagged(tag, token.value))


def _write_keyword(token, expect, f):
    return  _write(token, expect, f, KEYWORD)


def _write_symbol(token, expect, f):
    return  _write(token, expect, f, SYMBOL)


def _write_int_val(token, f):
    return _write(token, expect, f, INT_VAL)


def _write_string_val(token, f):
    return _write(token, expect, f, STRING_VAL)


def _write_identifier(token, f):
    if token.type != IDENTIFIER:
        f.seek(0)
        print(f.read())
        raise CompilationException(
            f'Expected an {IDENTIFIER}, found {token.type}: "{token.value}"'
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


class IndentingFile(object):

    def __init__(self, f):
        self._f = f
        self._indent = 0

    def updent(self):
        self._indent += 1

    def dedent(self):
        self._indent -= 1

    def write(self, data):
        for _ in range(self._indent):
            self._f.write('\t')
        self._f.write(data)


class CompilationEngine(object):

    class _new_xml_section(object):

        def __init__(slf, section_name):
            slf._section_name = section_name

        def __call__(slf, fn):

            def _wrapped(*args, **kwargs):
                f = args[1]
                f.write(_o_tag(slf._section_name) + '\n')
                f.updent()
                ret = fn(*args, **kwargs)
                f.dedent()
                f.write(_c_tag(slf._section_name) + '\n')
                return ret

            return _wrapped

    def __init__(self, jack_fname):
        self._jack_fname = jack_fname

    def compile(self, out_fname):
        tknizer = Tokenizer(self._jack_fname)
        with open(out_fname, 'w+') as f:
            self._compile_tokens(IndentingFile(f), tknizer)

    @_new_xml_section('tokens')
    def _compile_tokens(self, f, tknizer):
        nxt_token = self._compile_class(f, tknizer, tknizer.next_token())
        if nxt_token:
            raise CompilationException(
                f'Expected end of file, found {next_token}'
            )

    @_new_xml_section('class')
    def _compile_class(self, f, tknizer, token):
        _write_keyword(token, 'class', f)
        _write_identifier(tknizer.next_token(), f)
        _write_symbol(tknizer.next_token(), '{', f)

        token = tknizer.next_token()
        while token.value in ['static', 'field']:
            token = self._compile_class_var_dec(f, tknizer, token)

        while token.value in ['constructor', 'function', 'method']:
            token = self._compile_subroutine_dec(f, tknizer, token)

        _write_symbol(token, '}', f)
        return tknizer.next_token()

    @_new_xml_section('classVarDec')
    def _compile_class_var_dec(self, f, tknizer, token):
        _write_keyword(token, ['static', 'field'], f)
        _write_type(tknizer.next_token(), f)
        _write_identifier(tknizer.next_token(), f)

        token = tknizer.next_token()
        while token.value == ',':
            _write_symbol(token, ',', f)
            _write_identifier(tknizer.next_token(), f)
            token = tknizer.next_token()

        _write_symbol(token, ';', f)
        return tknizer.next_token()

    @_new_xml_section('subroutineDec')
    def _compile_subroutine_dec(self, f, tknizer, token):
        _write_keyword(token, ['constructor', 'function', 'method'], f)
        _write_type(tknizer.next_token(), f, include_void=True)
        _write_identifier(tknizer.next_token(), f)
        _write_symbol(tknizer.next_token(), '(', f)

        token = self._compile_parameter_list(f, tknizer, tknizer.next_token())
        _write_symbol(token, ')', f)

        token = self._compile_subroutine_body(f, tknizer, tknizer.next_token())
        return token

    @_new_xml_section('parameterList')
    def _compile_parameter_list(self, f, tknizer, token):
        if not (
            token.value in ['int', 'char', 'boolean']
            or token.type == IDENTIFIER
        ):
            return token

        while True:
            _write_type(token, f)
            _write_identifier(tknizer.next_token(), f)

            token = tknizer.next_token()
            if token.value == ',':
                _write_symbol(token, ',', f)
                token = tknizer.next_token()
            else:
                return token

    @_new_xml_section('subroutineBody')
    def _compile_subroutine_body(self, f, tknizer, token):
        _write_symbol(token, '{', f)

        token = tknizer.next_token()
        while token.value == 'var':
            token = self._compile_var_dec(f, tknizer, token)

        token = self._compile_statements(f, tknizer, token)
        _write_symbol(token, '}', f)

        return tknizer.next_token()

    @_new_xml_section('varDec')
    def _compile_var_dec(self, f, tknizer, token):
        _write_keyword(token, 'var', f)
        _write_type(tknizer.next_token(), f)
        _write_identifier(tknizer.next_token(), f)
        token = tknizer.next_token()

        while token.value == ',':
            _write_symbol(token, ',', f)
            _write_identifier(tknizer.next_token(), f)
            token = tknizer.next_token()

        _write_symbol(token, ';', f)
        return tknizer.next_token()

    @_new_xml_section('statements')
    def _compile_statements(self, f, tknizer, token):
        while token.value in ['let', 'if', 'while', 'do', 'return']:
            method = getattr(self, f'_compile_{token.value}')
            token = method(f, tknizer, token)

        return token

    @_new_xml_section('letStatement')
    def _compile_let(self, f, tknizer, token):
        _write_keyword(token, 'let', f)
        _write_identifier(tknizer.next_token(), f)

        token = tknizer.next_token()
        if token.value == '[':
            _write_symbol(token, '[', f)
            token = self._compile_expression(f, tknizer, tknizer.next_token())
            _write_symbol(token, ']', f)
            token = tknizer.next_token()

        _write_symbol(token, '=', f)
        token = self._compile_expression(f, tknizer, tknizer.next_token())

        _write_symbol(token, ';', f)
        return tknizer.next_token()

    @_new_xml_section('ifStatement')
    def _compile_if(self, f, tknizer, token):
        _write_keyword(token, 'if', f)
        _write_symbol(tknizer.next_token(), '(', f)

        token = self._compile_expression(f, tknizer, tknizer.next_token())
        _write_symbol(token, ')', f)
        _write_symbol(tknizer.next_token(), '{', f)

        token = self._compile_statements(f, tknizer, tknizer.next_token())
        _write_symbol(token, '}', f)

        token = tknizer.next_token()
        if token.value == 'else':
            _write_keyword(token, 'else', f)

            _write_symbol(tknizer.next_token(), '{', f)

            token = self._compile_statements(f, tknizer, tknizer.next_token())
            _write_symbol(token, '}', f)
            token = tknizer.next_token()

        return token

    @_new_xml_section('whileStatement')
    def _compile_while(self, f, tknizer, token):
        _write_keyword(token, 'while', f)
        _write_symbol(tknizer.next_token(), '(', f)

        token = self._compile_expression(f, tknizer, tknizer.next_token())
        _write_symbol(token, ')', f)
        _write_symbol(tknizer.next_token(), '{', f)

        token = self._compile_statements(f, tknizer, tknizer.next_token())
        _write_symbol(token, '}', f)
        return tknizer.next_token()

    @_new_xml_section('doStatement')
    def _compile_do(self, f, tknizer, token):
        _write_keyword(token, 'do', f)

        token = self._compile_subroutine_call(f, tknizer, tknizer.next_token())
        _write_symbol(token, ';', f)
        return tknizer.next_token()

    @_new_xml_section('returnStatement')
    def _compile_return(self, f, tknizer, token):
        _write_keyword(token, 'return', f)
        token = tknizer.next_token()
        if token.value != ';':
            token = self._compile_expression(f, tknizer, token)

        _write_symbol(token, ';', f)
        return tknizer.next_token()

    @_new_xml_section('subroutineCall')
    def _compile_subroutine_call(self, f, tknizer, token):
        _write_identifier(token, f)
        token = tknizer.next_token()
        if token.value == '.':
            _write_symbol(token, '.', f)
            _write_identifier(tknizer.next_token(), f)

        _write_symbol(tknizer.next_token(), '(', f)
        token = self._compile_expression_list(f, tknizer, tknizer.next_token())
        _write_symbol(token, ')', f)

        return tknizer.next_token()

    @_new_xml_section('expressionList')
    def _compile_expression_list(self, f, tknizer, token):
        is_empty = True
        if token.type in [INT_VAL, STRING_VAL]:
            is_empty = False
        elif token.type == KEYWORD and token.value in [TRUE, FALSE, NULL, THIS]:
            is_empty = False
        elif token.value == '(':
            is_empty = False
        elif token.value in ['-', '~']:
            is_empty = False
        else:
            next_token = tknizer.next_token()
            tknizer.rewind()
            if next_token.value == '[':
                is_empty = False
            elif next_token.value in ['(', '.']:
                is_empty = False
            elif next_token.type == IDENTIFIER:
                is_empty = False

        if is_empty:
            return token

        token = self._compile_expression(f, tknizer, token)
        while token == ',':
            _write_symbol(token, ',', f)
            token = self._compile_expression(f, tknizer, token)

        return token

    @_new_xml_section('expression')
    def _compile_expression(self, f, tknizer, token):
        token = self._compile_term(f, tknizer, token)
        ops = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
        while token.value in ops:
            _write_symbol(token, ops, f)
            token = self._compile_term(f, tknizer, tknizer.next_token())

        return token

    @_new_xml_section('term')
    def _compile_term(self, f, tknizer, token):
        if token.type == INT_VAL:
            _write_int_val(token, f)
            return tknizer.next_token()
        elif token.type == STRING_VAL:
            _write_string_val(token, f)
            return tknizer.next_token()
        elif token.type == KEYWORD and token.value in [TRUE, FALSE, NULL, THIS]:
            _write_keyword(token, [TRUE, FALSE, NULL, THIS], f)
            return tknizer.next_token()
        elif token.value == '(':
            _write_symbol(token, '(', f)
            token = self._compile_expression(f, tknizer, tknizer.next_token())
            _write_symbol(token, ')', f)
            return tknizer.next_token()
        elif token.value in ['-', '~']:
            _write_symbol(token, ['-', '~'], f)
            token = self._compile_term(f, tnkizer, tknizer.next_token())
            return token
        else:
            next_token = tknizer.next_token()
            if next_token.value == '[':
                _write_identifier(token, f)
                _write_symbol(next_token, '[', f)
                token = self._compsile_expression(
                    f, tknizer, tknizer.next_token()
                )
                _write_symbol(token, ']', f)
                return tknizer.next_token()
            elif next_token.value in ['(', '.']:
                tknizer.rewind()
                return self._compile_subroutine_call(f, tknizer, token)
            else:
                _write_identifier(token, f)
                return next_token
