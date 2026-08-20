
from king import King
from queen import Queen
from knight import Knight
from rook import Rook
from bishop import Bishop
from pawn import Pawn
from constants import PieceType
from moves import ChessPosition

class PieceFactory:
    @staticmethod
    def create(piece_type: str, position: ChessPosition, color):
        if piece_type == PieceType.KING:
            return King(position, color)

        if piece_type == PieceType.QUEEN:
            return Queen(position, color)

        if piece_type == PieceType.KNIGHT:
            return Knight(position, color)

        if piece_type == PieceType.ROOK:
            return Rook(position, color)

        if piece_type == PieceType.BISHOP:
            return Bishop(position, color)

        if piece_type == PieceType.PAWN:
            return Pawn(position, color)