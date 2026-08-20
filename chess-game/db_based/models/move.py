# ==========================================
# Move Representation & Algebraic Logger
# ==========================================
from typing import Optional
from db_based.models.piece import Piece, Pawn
from db_based.constant.constant import Position

class Move:
    def __init__(self, piece: Piece, start: Position, end: Position, captured_piece: Optional[Piece] = None):
        self.piece = piece
        self.start = start
        self.end = end
        self.captured_piece = captured_piece
        self.notation = self._generate_notation()

    def _generate_notation(self) -> str:
        """Generates standard chess notation (e.g., e4, Nf3, Bxf7)"""
        is_capture = self.captured_piece is not None
        capture_str = "x" if is_capture else ""

        # Pawn movement handling
        if isinstance(self.piece, Pawn):
            if is_capture:
                # Pawn captures record origin file (e.g., "exd5")
                return f"{Position.FILES[self.start.y]}x{self.end.to_algebraic()}"
            return self.end.to_algebraic()

        # Piece movement (e.g., "Nf3", "Bxf7")
        return f"{self.piece.symbol}{capture_str}{self.end.to_algebraic()}"
