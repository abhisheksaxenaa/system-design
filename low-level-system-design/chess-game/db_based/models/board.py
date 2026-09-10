# ==========================================
# Board Domain Model
# ==========================================
from typing import List, Optional
from db_based.models.piece import Piece, Pawn, Rook, Knight
from db_based.constant.constant import Position
from db_based.constant.constant import Color
from db_based.models.move import Move

class Board:
    def __init__(self):
        self.grid: List[List[Optional[Piece]]] = [[None for _ in range(8)] for _ in range(8)]
        self._initialize_board()

    def _initialize_board(self):
        # White Pieces
        self.grid[0][0] = Rook(Color.WHITE, Position(0, 0))
        self.grid[0][1] = Knight(Color.WHITE, Position(0, 1))
        for y in range(8):
            self.grid[1][y] = Pawn(Color.WHITE, Position(1, y))

        # Black Pieces
        self.grid[7][0] = Rook(Color.BLACK, Position(7, 0))
        self.grid[7][1] = Knight(Color.BLACK, Position(7, 1))
        for y in range(8):
            self.grid[6][y] = Pawn(Color.BLACK, Position(6, y))

    def get_piece(self, pos: Position) -> Optional[Piece]:
        return self.grid[pos.x][pos.y]

    def move_piece(self, start: Position, end: Position) -> Move:
        piece = self.get_piece(start)
        captured = self.get_piece(end)

        move_event = Move(piece, start, end, captured)

        piece.position = end
        self.grid[end.x][end.y] = piece
        self.grid[start.x][start.y] = None

        return move_event

