import argparse

from runner import Runner


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Translate input file into hack assembly code.'
    )
    parser.add_argument(
        'input_file',
        help='Name of vm file to convert.'
    )
    parser.add_argument(
        '--output-file',
        default=None,
        help='Name of output assembly file. Defaults to <input-suffix>.asm'
    )
    args = parser.parse_args()
    input_fname = args.input_file
    output_fname = args.output_file
    if not input_fname.endswith('.vm'):
        raise ValueError('Input file must be .vm')

    if not output_fname:
        output_fname = input_fname[:-2] + 'asm'

    Runner(input_fname).run(output_fname)
