from pieces import Piece
from board import ChessBoard

class Bishop(Piece):
    BEAM_INCREMENTS = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

    def get_threatened_positions(self, board: ChessBoard):
        positions = []
        for increment in Bishop.BEAM_INCREMENTS:
            positions += board.beam_search_threat(self._position, self._color, increment[0], increment[1])
        return positions

    def get_moveable_positions(self, board: ChessBoard):
        return self.get_threatened_positions(board)

    def _symbol_impl(self):
        return 'BI'