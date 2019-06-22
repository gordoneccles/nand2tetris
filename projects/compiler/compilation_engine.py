from symbol_table import SymbolTable
from tokenizer import (
    Tokenizer,
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


def _assert(token, expect):
    if isinstance(expect, list):
        if token.value not in expect:
            raise CompilationException(
                f'Expected "{expect}", found "{token.value}".'
            )
    elif token.value != expect:
        raise CompilationException(
            f'Expected "{expect}", found "{token.value}".'
        )


def _assert_identifier(token):
    if token.type != IDENTIFIER:
        raise CompilationException(
            f'Expected an {IDENTIFIER}, found {token.type}: "{token.value}"'
        )


def _assert_type(token, allow_void=False):
    type_keywords = ["int", "char", "boolean"]
    if allow_void:
        type_keywords.append("void")

    _assert(token, type_keywords)


class BufferingWriter(object):
    def __init__(self, writer):
        self._queued_writes = []
        self._writer = writer

    def buffer(self, method_name, *args, **kwargs):
        self._queued_writes.append((method_name, args, kwargs))

    def flush(self):
        for method_name, args, kwargs in self._queued_writes:
            method = getattr(self._writer, method_name)
            method(*args, **kwargs)
        self._queued_writes = []

    def __getattr__(self, name):
        if hasattr(self._writer, name):
            return getattr(self._writer, name)
        else:
            raise AssertionError(
                f"{self.__class__.__name__} object has no attribute {name}"
            )


class CompilationEngine(object):
    def __init__(self, jack_fname):
        self._jack_fname = jack_fname
        self._s_table = SymbolTable()
        self._writer = None
        self._class_name = None
        self._is_writing_void_func = None
        self.self._n_labels = 0

    def compile(self, out_fname):
        tknizer = Tokenizer(self._jack_fname)
        with VMWriter(out_fname) as writer:
            self._writer = BufferingWriter(writer)
            nxt_token = self._compile_class(tknizer, tknizer.next_token())
            if nxt_token:
                raise CompilationException(
                    f"Expected end of file, found {nxt_token}"
                )

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
        self._record_symbol(tknizer.next_token(), var_type, kind)

        token = tknizer.next_token()
        while token.value == ",":
            self._record_symbol(tknizer.next_token(), var_type, kind)
            token = tknizer.next_token()

        _assert(token, ";")
        return tknizer.next_token()

    def _compile_subroutine_dec(self, tknizer, token):
        _assert(token, ["constructor", "function", "method"])
        subroutine_type = token.value

        token = tknizer.next_token()
        _assert_type(token, allow_void=True)
        self._is_writing_void_func = token.value == "void"
        self._s_table.start_subroutine(is_method=subroutine_type == "method")

        token = tknizer.next_token()
        _assert_identifier(token)
        subroutine_name = token.value

        _assert(tknizer.next_token(), "(")
        # populates symbol table with arguments
        token = self._compile_parameter_list(tknizer, tknizer.next_token())
        _assert(token, ")")

        _assert(token, "{")
        token = tknizer.next_token()
        while token.value == "var":
            # populates symbol table with local variabls
            token = self._compile_var_dec(tknizer, token)

        n_locals = self._s_table.var_count(SymbolTable.VAR)
        qualified_name = ".".join(self._class_name, subroutine_name)
        self._writer.write_function(qualified_name, n_locals)

        if subroutine_type == "constructor":
            size = self._s_table.var_count(SymbolTable.FIELD)
            self._writer.write_push("constant", size)
            self._writer.write_call("Memory.alloc", 1)
            self._writer.write_pop("pointer", 0)
        elif subroutine_type == "method":
            self._writer.write_push("argument", 0)
            self._writer.write_pop("pointer", 0)

        token = self._compile_statements(tknizer, token)
        _assert(token, "}")
        self._is_writing_void_func = None
        self._s_table.complete_subroutine()

        return tknizer.next_token()

    def _compile_parameter_list(self, tknizer, token):
        if not (
            token.value in ["int", "char", "boolean"]
            or token.type == IDENTIFIER
        ):
            return token

        var_type = token.value
        token = tknizer.next_token()
        while True:
            self._record_symbol(token, var_type, SymbolTable.ARG)

            token = tknizer.next_token()
            if token.value == ",":
                token = tknizer.next_token()
            else:
                return token

    def _compile_var_dec(self, tknizer, token):
        _assert(token, "var")
        token = tknizer.next_token()
        _assert_type(token)
        var_type = token.value
        token = tknizer.next_token()
        self._record_symbol(token, var_type, SymbolTable.VAR)

        token = tknizer.next_token()
        while token.value == ",":
            self._record_symbol(tknizer.next_token(), var_type, SymbolTable.VAR)
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
            self._push_variable(var_name)
            self._writer.write_add()
            self._writer.write_pop("pointer", 1)

            _assert(tknizer.next_token(), "=")
            token = self._compile_expression(tknizer, tknizer.next_token())
            self._writer.write_pop("that", 0)
        else:
            _assert(token, "=")
            token = self._compile_expression(tknizer, tknizer.next_token())
            idx = self._s_table.index_of(var_name)
            kind = self._s_table.kind_of(var_name)
            self._writer.write_pop(kind, idx)

        _assert(token, ";")
        return tknizer.next_token()

    def _compile_if(self, f, tknizer, token):
        _assert(token, "if")
        _assert(tknizer.next_token(), "(")
        token = self._compile_expression(f, tknizer, tknizer.next_token())
        _assert(token, ")")
        _assert(tknizer.next_token(), "{")

        self._writer.write_not()
        false_label = self._allocate_label("IF_FALSE")
        self._writer.write_if(false_label)

        token = self._compile_statements(tknizer, tknizer.next_token())
        _assert(token, "}")

        token = tknizer.next_token()
        if token.value == "else":
            skip_else_label = self._allocate_label("SKIP_ELSE")
            self._writer.write_goto(skip_else_label)
            self._writer.write_label(false_label)
            _assert(tknizer.next_token(), "{")
            token = self._compile_statements(tknizer, tknizer.next_token())
            _assert(token, "}")
            token = tknizer.next_token()
            self._writer.write_label(skip_else_label)
        else:
            self._writer.write_label(false_label)

        return token

    def _compile_while(self, tknizer, token):
        _assert(token, "while")
        _assert(tknizer.next_token(), "(")
        true_label = self._allocate_label("WHILE_TRUE")
        self._writer.write_label(true_label)

        token = self._compile_expression(tknizer, tknizer.next_token())
        _assert(token, ")")
        _assert(tknizer.next_token(), "{")

        self._writer.write_not()
        false_label = self._allocate_label("WHILE_FALSE")
        self._writer.write_if(false_label)

        token = self._compile_statements(tknizer, tknizer.next_token())
        _assert(token, "}")
        self._writer.write_goto(true_label)
        return tknizer.next_token()

    def _compile_do(self, tknizer, token):
        _assert(token, "do")
        token = self._compile_subroutine_call(tknizer, tknizer.next_token())
        _assert(token, ";")
        self._writer.write_pop("temp", 0)
        return tknizer.next_token()

    def _compile_return(self, tknizer, token):
        _assert(token, "return")
        token = tknizer.next_token()
        if self._is_writing_void_func is True:
            _assert(token, ";")
            self._writer.write_push("constant", 0)
        elif self._is_writing_void_func is False:
            token = self._compile_expression(tknizer, token)
            _assert(token, ";")
        else:
            raise CompilationEngine(
                "Encountered return statement outside function"
            )
        self._writer.write_return()

        return tknizer.next_token()

    def _compile_subroutine_call(self, tknizer, token):
        _assert_identifier(token)
        token = tknizer.next_token()
        first_arg_var = "this"
        cls_name = self._class_name
        subroutine_name = token.value
        last_val = token.value

        if token.value == ".":
            token = tknizer.next_token()
            _assert_identifier(token)
            if self._s_table.has(last_val):
                cls_name = self._s_table.type_of(last_val)
                first_arg_var = cls_name
            else:
                # Assume either a constructor or class function
                first_arg_var = None
            token = tknizer.next_token()

        subroutine_name = ".".join([cls_name, subroutine_name])
        if first_arg_var == "this":
            self._writer.write_push("pointer", 0)
        elif first_arg_var:
            self._push_variable(first_arg_var)

        _assert(token, "(")
        n_args = 0
        token = tknizer.next_token()
        if token.value != ")":
            token = self._compile_expression(tknizer, tknizer.next_token())
            n_args += 1
            while token.value == ",":
                token = self._compile_expression(tknizer, tknizer.next_token())
                n_args += 1

        _assert(token, ")")
        if first_arg_var:
            n_args += 1
        self._writer.write_call(subroutine_name, n_args)

        return tknizer.next_token()

    def _compile_expression(self, tknizer, token):
        token = self._compile_term(tknizer, token)
        ops = ["+", "-", "*", "/", "&", "|", "<", ">", "="]
        while token.value in ops:
            op = token.value
            token = self._compile_term(tknizer, tknizer.next_token())
            if op == "+":
                self._writer.write_add()
            elif op == "-":
                self._writer.write_sub()
            elif op == "*":
                self._writer.write_call("Math.multiply", 2)
            elif op == "/":
                self._writer.write_call("Math.divide", 2)
            elif op == "&":
                self._writer.write_and()
            elif op == "|":
                self._writer.write_or()
            elif op == "<":
                self._writer.write_less_than()
            elif op == ">":
                self._writer.write_greater_than()
            elif op == "=":
                self._writer.write_equals()
            else:
                raise Exception(f"Bug: no case for op {token.value}")

        return token

    def _compile_term(self, tknizer, token):
        if token.type == INT_CONSTANT:
            if int(token.value) > 32767:
                raise CompilationException(f"Integer overflow: {token.value}")
            self._writer.write_push("constant", token.value)
            return tknizer.next_token()
        elif token.type == STRING_CONSTANT:
            # TODO: write string
            raise NotImplementedError()
            return tknizer.next_token()
        elif token.type == KEYWORD and token.value in [TRUE, FALSE, NULL, THIS]:
            if token.value == TRUE:
                self._writer.write_push("constant", 1)
                self._writer.write_neg()
            elif token.value in [FALSE, NULL]:
                self._writer.write_push("constant", 0)
            elif token.value == THIS:
                self._writer.write_push("argument", 0)
            else:
                raise Exception(f"Bug: unexpected keyword {token.value}")
            return tknizer.next_token()
        elif token.value == "(":
            token = self._compile_expression(tknizer, tknizer.next_token())
            _assert(token, ")")
            return tknizer.next_token()
        elif token.value in ["-", "~"]:
            next_token = self._compile_term(tknizer, tknizer.next_token())
            if token.value == "-":
                self._writer.write_neg()
            elif token.value == "~":
                self._writer.write_not()
            else:
                raise CompilationException(
                    f"Bug: Unexpected unary op {token.value}"
                )
            return next_token
        else:
            next_token = tknizer.next_token()
            if next_token.value == "[":
                _assert_identifier(token)
                array_var_name = token.value
                token = self._compile_expression(tknizer, tknizer.next_token())
                _assert(token, "]")
                self._push_variable(array_var_name)
                self._write_add()
                self._writer.write_pop("pointer", 1)
                self._writer.write_push("that", 0)
                return tknizer.next_token()
            elif next_token.value in ["(", "."]:
                tknizer.rewind()
                return self._compile_subroutine_call(tknizer, token)
            else:
                _assert_identifier(token)
                if not self._s_table.has(token.value):
                    raise CompilationException(
                        f"Unknown variable {token.value}"
                    )
                self._push_variable(token.value)
                return next_token

    def _push_variable(self, var_name):
        idx = self._s_table.index_of(var_name)
        kind = self._s_table.kind_of(var_name)
        if kind == SymbolTable.STATIC:
            self._writer.write_push("static", idx)
        elif kind == SymbolTable.FIELD:
            self._writer.write_push("this", idx)
        elif kind == SymbolTable.ARG:
            self._writer.write_push("argument", idx)
        elif kind == SymbolTable.VAR:
            self._writer.write_push("local", idx)
        else:
            raise Exception(f"Bug: unexpected variable kind {kind}")

    def _allocate_label(self, label_name):
        return ",".join([self._class_name, self._n_labels, label_name])
        self._n_labels += 1

    def _record_symbol(self, token, typ, kind):
        if token.type != IDENTIFIER:
            raise CompilationException(
                f"Expected an {IDENTIFIER}, "
                'found {token.type}: "{token.value}"'
            )
        self._s_table.define(token.value, typ, kind)
