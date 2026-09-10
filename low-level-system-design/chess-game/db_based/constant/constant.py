# ==========================================
# Enums and Coordinate Mapper
# ==========================================
from enum import Enum

class Color(Enum):
    WHITE = "WHITE"
    BLACK = "BLACK"


class GameStatus(Enum):
    ACTIVE = "ACTIVE"
    WHITE_WIN = "WHITE_WIN"
    BLACK_WIN = "BLACK_WIN"
    DRAW = "DRAW"


class Position:
    FILES = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

    def __init__(self, x: int, y: int):
        if not (0 <= x < 8 and 0 <= y < 8):
            raise ValueError("Position must be within board limits (0-7).")
        self.x = x  # Row (0-7)
        self.y = y  # Column (0-7)

    @classmethod
    def from_algebraic(cls, square: str) -> 'Position':
        """Converts string like 'e4' to Position(3, 4)"""
        col = cls.FILES.index(square[0].lower())
        row = int(square[1]) - 1
        return cls(row, col)

    def to_algebraic(self) -> str:
        """Converts Position(3, 4) to 'e4'"""
        return f"{self.FILES[self.y]}{self.x + 1}"

    def __eq__(self, other):
        return isinstance(other, Position) and self.x == other.x and self.y == other.y
