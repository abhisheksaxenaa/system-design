from abc import ABC, abstractmethod
from typing import List
from app.models.models import Symbol


class WinningStrategy:
    def check_winner(self, board: List[List[Symbol]], row: int, col: int, symbol: Symbol) -> bool:
        raise NotImplementedError

class Standard3x3WinningStrategy(WinningStrategy):
    def check_winner(self, board: List[List[Symbol]], row: int, col: int, symbol: Symbol) -> bool:
        size = 3
        # Check Row
        if all(board[row][c] == symbol for c in range(size)):
            return True
        # Check Column
        if all(board[r][col] == symbol for r in range(size)):
            return True
        # Check Diagonal
        if row == col and all(board[i][i] == symbol for i in range(size)):
            return True
        # Check Anti-Diagonal
        if row + col == size - 1 and all(board[i][size - 1 - i] == symbol for i in range(size)):
            return True
        return False

class Board:
    def __init__(self, size: int = 3):
        self.size = size
        self.grid: List[List[Symbol]] = [[Symbol.EMPTY for _ in range(size)] for _ in range(size)]

    def make_move(self, row: int, col: int, symbol: Symbol) -> bool:
        if 0 <= row < self.size and 0 <= col < self.size and self.grid[row][col] == Symbol.EMPTY:
            self.grid[row][col] = symbol
            return True
        return False

    def is_full(self) -> bool:
        return all(cell != Symbol.EMPTY for row in self.grid for cell in row)

    def to_json(self) -> str:
        return json.dumps([[cell.value for cell in row] for row in self.grid])

    @classmethod
    def from_json(cls, json_str: str) -> 'Board':
        data = json.loads(json_str)
        board = cls(len(data))
        board.grid = [[Symbol(cell) for cell in row] for row in data]
        return board