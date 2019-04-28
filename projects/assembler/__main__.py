import argparse

from runner import Runner


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Assemble input file into hack machine code.'
    )
    parser.add_argument(
        'input_file',
        help='Name of assembly file to convert.'
    )
    args = parser.parse_args()
    input_fname = args.input_file
    if not input_fname.endswith('.asm'):
        raise ValueError('Input file must be .asm')

    output_fname = input_fname[:-3] + 'hack'

    Runner(input_fname).run(output_fname)
