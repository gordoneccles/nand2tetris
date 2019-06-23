from glob import glob
import os

from compilation_engine import CompilationEngine


class Runner(object):
    def __init__(self, input_fname):
        self._in_fname = input_fname

    def run(self):
        if os.path.isdir(self._in_fname):
            jack_fnames = glob(os.path.join(self._in_fname, "*.jack"))
        else:
            jack_fnames = [self._in_fname]

        for jack_fname in jack_fnames:
            out_fname = jack_fname[:-5] + ".vm"
            CompilationEngine(jack_fname).compile(out_fname)
