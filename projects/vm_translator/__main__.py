import argparse
import os

from runner import Runner


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Translate input file into hack assembly code.'
    )
    parser.add_argument(
        'input_file',
        help='Name of vm file to convert.'
    )
    args = parser.parse_args()
    input_fname = args.input_file
    if os.path.isfile(input_fname):
        if not input_fname.endswith('.vm'):
            raise ValueError('Input file must be .vm')
        output_fname = input_fname[:-2] + 'asm'
    elif os.path.isdir(input_fname):
        output_fname = os.path.join(
            input_fname,
            os.path.basename(input_fname.rstrip('/')) + '.asm',
        )

    Runner(input_fname).run(output_fname)
