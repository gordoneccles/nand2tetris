import argparse
import os

from runner import Runner


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compile input jack file(s) into VM files"
    )
    parser.add_argument(
        "input_file",
        help="Name of jack file to comile, or directory with jack files.",
    )
    args = parser.parse_args()
    input_fname = args.input_file
    if os.path.isfile(input_fname) and not input_fname.endswith(".jack"):
        raise ValueError("Input file must be .jack")
    elif os.path.isdir(input_fname) and not any(
        f.endswith(".jack") for f in os.listdir(input_fname)
    ):
        raise ValueError("Directory contains no .jack files")

    Runner(input_fname).run()
