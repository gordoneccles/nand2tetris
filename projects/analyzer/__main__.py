import argparse
import os

from runner import Runner


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Analyze input file(s) and produce XML as output'
    )
    parser.add_argument(
        'input_file',
        help='Name of jack file to analyze.'
    )
    args = parser.parse_args()
    input_fname = args.input_file
    if os.path.isfile(input_fname) and not input_fname.endswith('.jack'):
        raise ValueError('Input file must be .jack')
    elif os.path.isdir(input_fname) and not any(
        f.endwith('.jack') for f in os.listdir(input_name)
    ):
        raise ValueError('Directory contains no .jack files')

    Runner(input_fname).run()
