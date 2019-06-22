from io import StringIO


class VMWriter(object):
    def __init__(self, fname):
        self._fname = fname
        self._f = None
        self._delay_buffer = StringIO()

    def __enter__(self):
        self._f = open(self._name, "w")
        return self

    def __exit__(self, *args, **kwargs):
        self._f.close()

    def flush_delayed(self) -> None:
        self._delay_buffer.seek(0)
        self._f.write(self._delay_buffer.read())
        self._delay_buffer.truncate()

    def write_push(self, segment: str, index: int) -> None:
        self._f.write("push {segment} {index}\n")

    def write_pop(self, segment: str, index: int) -> None:
        self._f.write(f"pop {segment} {index}\n")

    def write_add(self) -> None:
        self._f.write("add\n")

    def write_sub(self) -> None:
        self._f.write("sub\n")

    def write_neg(self) -> None:
        self._f.write("neg\n")

    def write_equals(self) -> None:
        self._f.write("eq\n")

    def write_greater_than(self) -> None:
        self._f.write("gt\n")

    def write_less_than(self) -> None:
        self._f.write("lt\n")

    def write_and(self) -> None:
        self._f.write("and\n")

    def write_or(self) -> None:
        self._f.write("or\n")

    def write_not(self) -> None:
        self._f.write("not\n")

    def write_label(self, label: str) -> None:
        self._f.write(f"label {label}\n")

    def write_goto(self, label: str) -> None:
        self._f.write(f"goto {label}\n")

    def write_if(self, label: str) -> None:
        self._f.write(f"if-goto {label}\n")

    def write_call(self, name: str, n_args: int) -> None:
        self._f.write(f"call {name} {n_args}\n")

    def write_function(self, name: str, n_locals: int) -> None:
        self._f.write(f"function {name} {n_locals}\n")

    def write_return(self) -> None:
        self._f.write(f"call\n")

    def _write(self, data, delayed=False) -> None:
        if delayed:
            self._delay_buffer.write(data)
        else:
            self._f.write(data)
