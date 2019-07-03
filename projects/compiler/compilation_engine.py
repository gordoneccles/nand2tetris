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
    CLASS,
    STATIC,
    FIELD,
    METHOD,
    FUNCTION,
    CONSTRUCTOR,
    INT,
    BOOLEAN,
    CHAR,
    VOID,
    VAR,
    LET,
    DO,
    IF,
    ELSE,
    WHILE,
    RETURN,
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
    type_keywords = [INT, CHAR, BOOLEAN]
    if allow_void:
        type_keywords.append(VOID)
    if token.value not in type_keywords and token.type != IDENTIFIER:
        raise CompilationException(
            "Expected a primitive type or identifier, "
            f'found {token.type}: "{token.value}"'
        )


class CompilationEngine(object):
    def __init__(self, jack_fname):
        self._jack_fname = jack_fname
        self._s_table = SymbolTable()
        self._writer = None
        self._class_name = None
        self._is_writing_void_func = None
        self._current_func_name = None
        self._n_labels = 0

    def compile(self, out_fname: str) -> None:
        tknizer = Tokenizer(self._jack_fname)
        with VMWriter(out_fname) as writer:
            self._writer = writer
            token = self._compile_class(tknizer, tknizer.next_token())
            if token:
                raise CompilationException(
                    f"Expected end of file, found {token}"
                )

    def _compile_class(self, tknizer, token):
        _assert(token, CLASS)
        token = tknizer.next_token()
        _assert_identifier(token)
        self._class_name = token.value
        _assert(tknizer.next_token(), "{")

        token = tknizer.next_token()
        while token.value in [STATIC, FIELD]:
            token = self._compile_class_var_dec(tknizer, token)

        while token.value in [CONSTRUCTOR, FUNCTION, METHOD]:
            token = self._compile_subroutine_dec(tknizer, token)

        _assert(token, "}")
        return tknizer.next_token()

    def _compile_class_var_dec(self, tknizer, token):
        _assert(token, [STATIC, FIELD])
        if token.value == STATIC:
            kind = SymbolTable.STATIC
        else:
            kind = SymbolTable.FIELD

        token = tknizer.next_token()
        _assert_type(token)
        var_type = token.value
        self._record_symbol(tknizer.next_token(), var_type, kind)

        token = tknizer.next_token()
        while token.value == ",":
            self._record_symbol(tknizer.next_token(), var_type, kind)
            token = tknizer.next_token()

        _assert(token, ";")
        return tknizer.next_token()

    def _compile_subroutine_dec(self, tknizer, token):
        _assert(token, [CONSTRUCTOR, FUNCTION, METHOD])
        subroutine_type = token.value

        token = tknizer.next_token()
        _assert_type(token, allow_void=True)
        self._is_writing_void_func = token.value == VOID
        self._s_table.start_subroutine(is_method=subroutine_type == METHOD)

        token = tknizer.next_token()
        _assert_identifier(token)
        subroutine_name = token.value
        self._current_func_name = subroutine_name

        _assert(tknizer.next_token(), "(")
        # populates symbol table with arguments
        token = self._compile_parameter_list(tknizer, tknizer.next_token())
        _assert(token, ")")

        _assert(tknizer.next_token(), "{")
        token = tknizer.next_token()
        while token.value == VAR:
            # populates symbol table with local variabls
            token = self._compile_var_dec(tknizer, token)

        n_locals = self._s_table.var_count(SymbolTable.VAR)
        qualified_name = ".".join([self._class_name, subroutine_name])
        self._writer.write_function(qualified_name, n_locals)

        if subroutine_type == CONSTRUCTOR:
            size = self._s_table.var_count(SymbolTable.FIELD)
            self._writer.write_push("constant", size)
            self._writer.write_call("Memory.alloc", 1)
            self._writer.write_pop("pointer", 0)
        elif subroutine_type == METHOD:
            self._writer.write_push("argument", 0)
            self._writer.write_pop("pointer", 0)

        token = self._compile_statements(tknizer, token)
        _assert(token, "}")
        self._is_writing_void_func = None
        self._s_table.complete_subroutine()

        return tknizer.next_token()

    def _compile_parameter_list(self, tknizer, token):
        if not (
            token.value in [INT, CHAR, BOOLEAN] or token.type == IDENTIFIER
        ):
            return token

        while True:
            var_type = token.value
            self._record_symbol(tknizer.next_token(), var_type, SymbolTable.ARG)
            token = tknizer.next_token()
            if token.value == ",":
                token = tknizer.next_token()
            else:
                return token

    def _compile_var_dec(self, tknizer, token):
        _assert(token, VAR)
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
        while token.value in [LET, IF, WHILE, DO, RETURN]:
            method = getattr(self, f"_compile_{token.value}")
            token = method(tknizer, token)

        return token

    def _compile_let(self, tknizer, token):
        _assert(token, LET)
        token = tknizer.next_token()
        _assert_identifier(token)
        var_name = token.value

        token = tknizer.next_token()
        if token.value == "[":
            token = self._compile_expression(tknizer, tknizer.next_token())
            _assert(token, "]")
            self._push_variable(var_name)
            self._writer.write_add()

            _assert(tknizer.next_token(), "=")
            token = self._compile_expression(tknizer, tknizer.next_token())
            self._writer.write_pop("temp", 0)
            self._writer.write_pop("pointer", 1)
            self._writer.write_push("temp", 0)
            self._writer.write_pop("that", 0)
        else:
            _assert(token, "=")
            token = self._compile_expression(tknizer, tknizer.next_token())
            self._pop_variable(var_name)

        _assert(token, ";")
        return tknizer.next_token()

    def _compile_if(self, tknizer, token):
        _assert(token, IF)
        _assert(tknizer.next_token(), "(")
        token = self._compile_expression(tknizer, tknizer.next_token())
        _assert(token, ")")
        _assert(tknizer.next_token(), "{")

        self._writer.write_push("constant", 0)
        self._writer.write_equals()
        false_label = self._allocate_label("IF_FALSE")
        self._writer.write_if(false_label)

        token = self._compile_statements(tknizer, tknizer.next_token())
        _assert(token, "}")

        token = tknizer.next_token()
        if token.value == ELSE:
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
        _assert(token, WHILE)
        _assert(tknizer.next_token(), "(")
        true_label = self._allocate_label("WHILE_TRUE")
        self._writer.write_label(true_label)

        token = self._compile_expression(tknizer, tknizer.next_token())
        _assert(token, ")")
        _assert(tknizer.next_token(), "{")

        self._writer.write_push("constant", 0)
        self._writer.write_equals()
        false_label = self._allocate_label("WHILE_FALSE")
        self._writer.write_if(false_label)

        token = self._compile_statements(tknizer, tknizer.next_token())
        _assert(token, "}")
        self._writer.write_goto(true_label)
        self._writer.write_label(false_label)
        return tknizer.next_token()

    def _compile_do(self, tknizer, token):
        _assert(token, DO)
        token = self._compile_subroutine_call(tknizer, tknizer.next_token())
        _assert(token, ";")
        self._writer.write_pop("temp", 0)
        return tknizer.next_token()

    def _compile_return(self, tknizer, token):
        _assert(token, RETURN)
        token = tknizer.next_token()
        if self._is_writing_void_func is True:
            _assert(token, ";")
            self._writer.write_push("constant", 0)
        elif self._is_writing_void_func is False:
            if token.value == THIS:
                self._writer.write_push("pointer", 0)
                token = tknizer.next_token()
            else:
                token = self._compile_expression(tknizer, token)
            _assert(token, ";")
        else:
            raise CompilationEngine(
                "Encountered return statement outside function"
            )
        self._writer.write_return()

        return tknizer.next_token()

    def _compile_subroutine_call(self, tknizer, first_token):
        _assert_identifier(first_token)

        is_method = False
        second_token = tknizer.next_token()
        if second_token.value == ".":
            token = tknizer.next_token()
            _assert_identifier(token)
            if self._s_table.has(first_token.value):
                # method call on another object
                is_method = True
                class_name = self._s_table.type_of(first_token.value)
                subroutine_name = ".".join([class_name, token.value])
                self._push_variable(first_token.value)
            else:
                # constructor or class function
                subroutine_name = ".".join([first_token.value, token.value])
            token = tknizer.next_token()
        else:
            # method call on this object
            is_method = True
            subroutine_name = ".".join([self._class_name, first_token.value])
            self._writer.write_push("pointer", 0)
            token = second_token

        _assert(token, "(")
        n_args = 1 if is_method else 0
        token = tknizer.next_token()
        if token.value != ")":
            token = self._compile_expression(tknizer, token)
            n_args += 1
            while token.value == ",":
                token = self._compile_expression(tknizer, tknizer.next_token())
                n_args += 1

        _assert(token, ")")
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
            self._writer.write_push("constant", token.value)
            return tknizer.next_token()
        elif token.type == STRING_CONSTANT:
            str_val = token.value[1:-1]
            self._writer.write_push("constant", len(str_val))
            self._writer.write_call("String.new", 1)
            for char in str_val:
                self._writer.write_push("constant", ord(char))
                self._writer.write_call("String.appendChar", 2)
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
                self._writer.write_add()
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
            self._writer.write_push(STATIC, idx)
        elif kind == SymbolTable.FIELD:
            self._writer.write_push(THIS, idx)
        elif kind == SymbolTable.ARG:
            self._writer.write_push("argument", idx)
        elif kind == SymbolTable.VAR:
            self._writer.write_push("local", idx)
        else:
            raise Exception(f"Bug: unexpected variable kind {kind}")

    def _pop_variable(self, var_name):
        idx = self._s_table.index_of(var_name)
        kind = self._s_table.kind_of(var_name)
        if kind == SymbolTable.STATIC:
            self._writer.write_pop(STATIC, idx)
        elif kind == SymbolTable.FIELD:
            self._writer.write_pop(THIS, idx)
        elif kind == SymbolTable.ARG:
            self._writer.write_pop("argument", idx)
        elif kind == SymbolTable.VAR:
            self._writer.write_pop("local", idx)
        else:
            raise Exception(f"Bug: unexpected variable kind {kind}")

    def _allocate_label(self, label_name):
        label = "{cls}.{func}${name}${id}".format(
            cls=self._class_name,
            func=self._current_func_name,
            name=label_name,
            id=self._n_labels,
        )
        self._n_labels += 1
        return label

    def _record_symbol(self, token, typ, kind):
        if token.type != IDENTIFIER:
            raise CompilationException(
                f"Expected an {IDENTIFIER}, "
                f'found {token.type}: "{token.value}"'
            )
        self._s_table.define(token.value, typ, kind)
