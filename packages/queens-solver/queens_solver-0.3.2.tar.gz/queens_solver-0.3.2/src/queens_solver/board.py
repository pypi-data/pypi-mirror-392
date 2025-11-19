import math
import seaborn as sns
from dataclasses import dataclass
from enum import Enum
from colored import Fore, Style

class SquareState(Enum):
    """
    Possible states for a square
    """

    UNKNOWN = "□"
    NOT_A_QUEEN = "*"
    QUEEN = "Q"


@dataclass
class Square:
    """
    Represent a square on the board
    """

    region: int
    state = SquareState.UNKNOWN

class Board:
    """
    Represent the queens board
    """

    def __init__(self, N: int) -> None:
        self.N = N
        self.squares: list[list[Square]] = [
            [Square(0) for _ in range(N)] for _ in range(N)
        ]
        # Generate a list of unique colors for each region
        self.colors = []
        palette = sns.color_palette(n_colors=N)
        for color in palette:
            # Convert values from float tuple to percentage tuple
            region_color = (f"{int(value * 100)}%" for value in color)
            self.colors.append(Fore.rgb(*region_color))

    def __str__(self) -> str:
        """
        Return a coloured string representation of the board
        """
        lines = []
        for n in range(self.N):
            line = [
                f"{self.colors[square.region]}{square.state.value}{Style.reset}"
                for square in self.squares[n]
            ]
            lines.append(" ".join(line))
        return "\n".join(lines)

    def in_bounds(self, row: int, col: int) -> bool:
        """
        Check if a given row and column is inside the board
        """
        if (0 <= row < self.N and 0 <= col < self.N):
            return True
        return False

    def get_square(self, row: int, col: int) -> Square:
        """
        Get the square at the given row and column
        """
        if not self.in_bounds(row, col):
            raise IndexError(
                f"({row}, {col}) out of bounds for {self.N}x{self.N} board"
            )
        return self.squares[row][col]

def board_parser(board_string: str) -> Board:
    """
    Parse a string representation of a board into a Board object
    """    
    cells = board_string.split(";")
    n_cells = len(cells)
    N = math.isqrt(n_cells)
    if N**2 != n_cells:
        raise ValueError(
            f"Invalid board string length. "
            f"Length must be a perfect square (e.g., 9, 16, 25), "
            f"but got {n_cells}."
        )

    try:
        board = Board(N)
        for i in range(N):
            for j in range(N):
                board.squares[i][j].region = int(cells[N * i + j])
    except ValueError as e:
        raise ValueError(
            f"Invalid region value in board string: {e}"
        ) from e

    return board
