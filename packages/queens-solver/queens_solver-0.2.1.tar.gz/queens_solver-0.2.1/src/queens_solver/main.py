import argparse
import queens_solver

def main():
    parser = argparse.ArgumentParser(
        prog=queens_solver.__pkg_name__,
        description=queens_solver.__description__
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=queens_solver.__version__
    )

    parser.parse_args()

    parser.print_help()

