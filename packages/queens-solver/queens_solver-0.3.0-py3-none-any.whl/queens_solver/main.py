import argparse
from . import __pkg_name__, __description__, __version__
from .board import board_parser
from .solver import Solver


def main() -> None:
    parser = argparse.ArgumentParser(prog=__pkg_name__, description=__description__)

    parser.add_argument(
        "-r",
        "--raw",
        help="enter a raw board string (semicolon-seperated region values). "
        'e.g. -r "0;1;2;3;0;1;2;3;0;1;2;3;0;1;2;3"',
        metavar="BOARD_STRING",
    )

    parser.add_argument("-v", "--version", action="version", version=__version__)

    args = parser.parse_args()

    if args.raw:
        board = board_parser(args.raw)

    else:
        board = board_parser(
            "0;0;0;0;0;0;1;"
            "0;2;3;4;4;4;1;"
            "0;2;3;3;3;4;1;"
            "0;2;2;6;3;4;1;"
            "0;5;2;6;6;6;1;"
            "0;5;5;5;5;6;1;"
            "0;1;1;1;1;1;1"
        )

    solver = Solver(board)
    solver.solve()
