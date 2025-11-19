from .board import Board, SquareState
import copy

class Solver:
    def __init__(self, board: Board) -> None:
        self.board = board
        self.solutions: list[Board] = []         

    def valid_placement(self, r: int, c: int) -> bool:
        # Check for a queen placed in the column above
        if SquareState.QUEEN in [row[c].state for row in self.board.squares[:r]]:
            return False

        diffs = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        for d_row, d_col in diffs:
            if not self.board.in_bounds(r + d_row, c + d_col):
                continue
            if self.board.get_square(r + d_row, c + d_col).state == SquareState.QUEEN:
                return False
        
        region = self.board.get_square(r, c).region
        for row in self.board.squares:
            if SquareState.QUEEN in [square.state for square in row if square.region == region]:
                return False

        return True
    
    def print_solution(self) -> None:
        solution_board = copy.deepcopy(self.board)
        for r in range(solution_board.N):
            for c in range(solution_board.N):
                if solution_board.get_square(r, c).state == SquareState.UNKNOWN:
                    solution_board.get_square(r, c).state = SquareState.NOT_A_QUEEN
        self.solutions.append(solution_board)
        print(solution_board)
    
    def place_queens(self, r: int) -> None:
        if r == self.board.N:
            print("\nSolution found:")
            self.print_solution()
            return
        
        for c in range(self.board.N):
            if self.valid_placement(r, c):
                self.board.squares[r][c].state = SquareState.QUEEN
                self.place_queens(r + 1)
                self.board.squares[r][c].state = SquareState.NOT_A_QUEEN

    def solve(self) -> None:
        print("Solving:")
        print(self.board)

        self.place_queens(0)
        if not self.solutions:
            print("No solutions found :(")
        
        
                

