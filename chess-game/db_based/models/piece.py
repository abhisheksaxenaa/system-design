
# ==========================================
# 2. Domain Entities with Symbol Representation
# ==========================================
import abc
from db_based.constant.constant import Position
from db_based.constant.constant import Color
# from db_based.models.board import Board


class Piece(abc.ABC):
    def __init__(self, color: Color, position: Position):
        self.color = color
        self.position = position
        self.symbol = ""  # P, N, B, R, Q, K

    @abc.abstractmethod
    def is_valid_move(self, target: Position, board: 'Board') -> bool:
        pass


class Pawn(Piece):
    def __init__(self, color: Color, position: Position):
        super().__init__(color, position)
        self.symbol = ""  # Pawns don't have a letter prefix in notation

    def is_valid_move(self, target: Position, board: 'Board') -> bool:
        direction = 1 if self.color == Color.WHITE else -1
        dx = target.x - self.position.x
        dy = target.y - self.position.y

        # Forward 1
        if dy == 0 and dx == direction:
            return board.get_piece(target) is None
        # Initial double step forward
        start_row = 1 if self.color == Color.WHITE else 6
        if dy == 0 and dx == 2 * direction and self.position.x == start_row:
            intermediate = Position(self.position.x + direction, self.position.y)
            return board.get_piece(intermediate) is None and board.get_piece(target) is None
        # Diagonal Capture
        if abs(dy) == 1 and dx == direction:
            dest_piece = board.get_piece(target)
            return dest_piece is not None and dest_piece.color != self.color

        return False


class Knight(Piece):
    def __init__(self, color: Color, position: Position):
        super().__init__(color, position)
        self.symbol = "N"

    def is_valid_move(self, target: Position, board: 'Board') -> bool:
        dx = abs(self.position.x - target.x)
        dy = abs(self.position.y - target.y)
        if (dx == 1 and dy == 2) or (dx == 2 and dy == 1):
            dest = board.get_piece(target)
            return dest is None or dest.color != self.color
        return False


class Rook(Piece):
    def __init__(self, color: Color, position: Position):
        super().__init__(color, position)
        self.symbol = "R"

    def is_valid_move(self, target: Position, board: 'Board') -> bool:
        if self.position.x != target.x and self.position.y != target.y:
            return False
        
        dx = 0 if target.x == self.position.x else (1 if target.x > self.position.x else -1)
        dy = 0 if target.y == self.position.y else (1 if target.y > self.position.y else -1)
        
        curr_x, curr_y = self.position.x + dx, self.position.y + dy
        while curr_x != target.x or curr_y != target.y:
            if board.get_piece(Position(curr_x, curr_y)) is not None:
                return False
            curr_x += dx
            curr_y += dy

        dest = board.get_piece(target)
        return dest is None or dest.color != self.color

