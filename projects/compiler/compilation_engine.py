import html

from symbol_table import SymbolTable
from tokenizer import (
    Tokenizer,
    SYMBOL,
    KEYWORD,
    STRING_CONSTANT,
    INT_CONSTANT,
    IDENTIFIER,
    TRUE,
    FALSE,
    NULL,
    THIS,
)
from vm_writer import VMWriter


class CompilationException(Exception):
    pass


def _o_tag(s):
    return f"<{s}>"


def _c_tag(s):
    return f"</{s}>"


def _tagged(tag_name, s):
    return f"{_o_tag(tag_name)}{s}{_c_tag(tag_name)}\n"


def _assert(token, expect):
    if isinstance(expect, list):
        if token.value not in expect:
            raise CompilationException(f'Expected "{expect}", found "{token.value}".')
    elif token.value != expect:
        raise CompilationException(f'Expected "{expect}", found "{token.value}".')


def _assert_identifier(token):
    if token.type != IDENTIFIER:
        raise CompilationException(
            f'Expected an {IDENTIFIER}, found {token.type}: "{token.value}"'
        )


def _write(token, expect, f, tag):
    if isinstance(expect, list):
        if token.value not in expect:
            raise CompilationException(f'Expected "{expect}", found "{token.value}".')
    elif token.value != expect:
        raise CompilationException(f'Expected "{expect}", found "{token.value}".')

    f.write(_tagged(tag, html.escape(token.value)))


def _write_keyword(token, expect, f):
    return _write(token, expect, f, KEYWORD)


def _write_symbol(token, expect, f):
    return _write(token, expect, f, SYMBOL)


def _write_int_val(token, f):
    return f.write(_tagged(INT_CONSTANT, html.escape(token.value)))


def _write_string_val(token, f):
    val = token.value[1:-1]
    return f.write(_tagged(STRING_CONSTANT, html.escape(val)))


def _write_identifier(token, f):
    if token.type != IDENTIFIER:
        raise CompilationException(
            f'Expected an {IDENTIFIER}, found {token.type}: "{token.value}"'
        )
    f.write(_tagged(IDENTIFIER, html.escape(token.value)))


def _assert_type(token, allow_void=False):
    type_keywords = ["int", "char", "boolean"]
    if allow_void:
        type_keywords.append("void")

    _assert(token, type_keywords)


def _write_type(token, f, include_void=False):
    type_keywords = ["int", "char", "boolean"]
    if include_void:
        type_keywords.append("void")

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
            self._f.write("\t")
        self._f.write(data)


class CompilationEngine(object):
    def __init__(self, jack_fname):
        self._jack_fname = jack_fname
        self._s_table = SymbolTable()
        self._writer = None
        self._class_name = None

    def compile(self, out_fname):
        tknizer = Tokenizer(self._jack_fname)
        with VMWriter(out_fname) as writer:
            self._writer = writer
            nxt_token = self._compile_class(tknizer, tknizer.next_token())
            if nxt_token:
                raise CompilationException(f"Expected end of file, found {nxt_token}")

    def _compile_class(self, tknizer, token):
        _assert(token, "class")
        token = tknizer.next_token()
        _assert_identifier(token)
        self._class_name = token.value
        _assert(tknizer.next_token(), "{")

        token = tknizer.next_token()
        while token.value in ["static", "field"]:
            token = self._compile_class_var_dec(tknizer, token)

        while token.value in ["constructor", "function", "method"]:
            token = self._compile_subroutine_dec(tknizer, token)

        _assert(token, "}")
        return tknizer.next_token()

    def _compile_class_var_dec(self, tknizer, token):
        _assert(token, ["static", "field"])
        if token.value == "static":
            kind = SymbolTable.STATIC
        else:
            kind = SymbolTable.FIELD

        var_type = tknizer.next_token()
        _assert_type(var_type)
        self._record_symbol(var_type, tknizer.next_token(), kind)

        token = tknizer.next_token()
        while token.value == ",":
            self._record_symbol(var_type, tknizer.next_token(), kind)
            token = tknizer.next_token()

        _assert(token, ";")
        return tknizer.next_token()

    def _compile_subroutine_dec(self, tknizer, token):
        _assert(token, ["constructor", "function", "method"])
        subroutine_type = token.value

        token = tknizer.next_token()
        _assert_type(token, allow_void=True)
        return_type = token.value
        self._s_table.start_subroutine()

        token = tknizer.next_token()
        _assert_identifier(token)
        subroutine_name = token.value

        _assert(tknizer.next_token(), "(")

        token = self._compile_parameter_list(tknizer, tknizer.next_token())
        _assert(token, ")")

        token = self._compile_subroutine_body(tknizer, tknizer.next_token())

        n_locals = self._s_table.var_count(SymbolTable.VAR)
        if subroutine_type in ["constructor", "method"]:
            n_locals += 1
        qualified_name = ".".join(self._class_name, subroutine_name)
        self._writer.write_function(qualified_name, n_locals)
        self._writer.flush_delayed()
        if return_type == "void":
            self._writer.write_push("constant", 0)

        return token

    def _compile_parameter_list(self, tknizer, token):
        if not (token.value in ["int", "char", "boolean"] or token.type == IDENTIFIER):
            return token

        var_type = token.value
        token = tknizer.next_token()
        while True:
            _assert_identifier(token)
            self._record_symbol(token, var_type, SymbolTable.ARG)

            token = tknizer.next_token()
            if token.value == ",":
                token = tknizer.next_token()
            else:
                return token

    def _compile_subroutine_body(self, tknizer, token):
        _assert(token, "{")

        token = tknizer.next_token()
        while token.value == "var":
            token = self._compile_var_dec(tknizer, token)

        token = self._compile_statements(tknizer, token)
        _assert(token, "}")

        return tknizer.next_token()

    def _compile_var_dec(self, tknizer, token):
        _assert(token, "var")
        token = tknizer.next_token()
        _assert_type(token)
        var_type = token.value
        token = tknizer.next_token()
        _assert_identifier(token)
        self._record_symbol(token, var_type, SymbolTable.VAR)

        token = tknizer.next_token()
        while token.value == ",":
            token = tknizer.next_token()
            _assert_identifier(token)
            self._record_symbol(token, var_type, SymbolTable.VAR)
            token = tknizer.next_token()

        _assert(token, ";")
        return tknizer.next_token()

    def _compile_statements(self, tknizer, token):
        while token.value in ["let", "if", "while", "do", "return"]:
            method = getattr(self, f"_compile_{token.value}")
            token = method(tknizer, token)

        return token

    def _compile_let(self, tknizer, token):
        _assert(token, "let")
        token = tknizer.next_token()
        _assert_identifier(token)
        var_name = token.value

        token = tknizer.next_token()
        if token.value == "[":
            token = self._compile_expression(tknizer, tknizer.next_token())
            _assert(token, "]")
            token = tknizer.next_token()

        _assert(token, "=")
        token = self._compile_expression(tknizer, tknizer.next_token())

        _assert(token, ";")
        return tknizer.next_token()

    def _compile_if(self, f, tknizer, token):
        _write_keyword(token, "if", f)
        _write_symbol(tknizer.next_token(), "(", f)

        token = self._compile_expression(f, tknizer, tknizer.next_token())
        _write_symbol(token, ")", f)
        _write_symbol(tknizer.next_token(), "{", f)

        token = self._compile_statements(f, tknizer, tknizer.next_token())
        _write_symbol(token, "}", f)

        token = tknizer.next_token()
        if token.value == "else":
            _write_keyword(token, "else", f)

            _write_symbol(tknizer.next_token(), "{", f)

            token = self._compile_statements(f, tknizer, tknizer.next_token())
            _write_symbol(token, "}", f)
            token = tknizer.next_token()

        return token

    def _compile_while(self, f, tknizer, token):
        _write_keyword(token, "while", f)
        _write_symbol(tknizer.next_token(), "(", f)

        token = self._compile_expression(f, tknizer, tknizer.next_token())
        _write_symbol(token, ")", f)
        _write_symbol(tknizer.next_token(), "{", f)

        token = self._compile_statements(f, tknizer, tknizer.next_token())
        _write_symbol(token, "}", f)
        return tknizer.next_token()

    def _compile_do(self, f, tknizer, token):
        _write_keyword(token, "do", f)

        token = self._compile_subroutine_call(f, tknizer, tknizer.next_token())
        _write_symbol(token, ";", f)
        return tknizer.next_token()

    def _compile_return(self, f, tknizer, token):
        _write_keyword(token, "return", f)
        token = tknizer.next_token()
        if token.value != ";":
            token = self._compile_expression(f, tknizer, token)

        _write_symbol(token, ";", f)
        return tknizer.next_token()

    def _compile_subroutine_call(self, f, tknizer, token):
        _write_identifier(token, f)
        token = tknizer.next_token()
        if token.value == ".":
            _write_symbol(token, ".", f)
            _write_identifier(tknizer.next_token(), f)
            token = tknizer.next_token()

        _write_symbol(token, "(", f)
        token = self._compile_expression_list(f, tknizer, tknizer.next_token())
        _write_symbol(token, ")", f)

        return tknizer.next_token()

    def _compile_expression(self, f, tknizer, token):
        token = self._compile_term(f, tknizer, token)
        ops = ["+", "-", "*", "/", "&", "|", "<", ">", "="]
        while token.value in ops:
            _write_symbol(token, ops, f)
            token = self._compile_term(f, tknizer, tknizer.next_token())

        return token

    def _compile_term(self, f, tknizer, token):
        if token.type == INT_CONSTANT:
            _write_int_val(token, f)
            return tknizer.next_token()
        elif token.type == STRING_CONSTANT:
            _write_string_val(token, f)
            return tknizer.next_token()
        elif token.type == KEYWORD and token.value in [TRUE, FALSE, NULL, THIS]:
            _write_keyword(token, [TRUE, FALSE, NULL, THIS], f)
            return tknizer.next_token()
        elif token.value == "(":
            _write_symbol(token, "(", f)
            token = self._compile_expression(f, tknizer, tknizer.next_token())
            _write_symbol(token, ")", f)
            return tknizer.next_token()
        elif token.value in ["-", "~"]:
            _write_symbol(token, ["-", "~"], f)
            token = self._compile_term(f, tknizer, tknizer.next_token())
            return token
        else:
            next_token = tknizer.next_token()
            if next_token.value == "[":
                _write_identifier(token, f)
                _write_symbol(next_token, "[", f)
                token = self._compile_expression(f, tknizer, tknizer.next_token())
                _write_symbol(token, "]", f)
                return tknizer.next_token()
            elif next_token.value in ["(", "."]:
                tknizer.rewind()
                return self._compile_subroutine_call(f, tknizer, token)
            else:
                _write_identifier(token, f)
                return next_token

    def _record_symbol(self, token, typ, kind):
        if token.type != IDENTIFIER:
            raise CompilationException(
                f"Expected an {IDENTIFIER}, " 'found {token.type}: "{token.value}"'
            )
        self._s_table.define(token.value, type, kind)
