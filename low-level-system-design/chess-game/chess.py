from typing import Optional, List
from db_based.repository.game_repository import GameRepository
from db_based.constant.constant import Position
from db_based.constant.constant import Color, GameStatus
from db_based.models.move import Move
from db_based.models.board import Board

# ==========================================
# Service Controller (Accepting Standard Notation)
# ==========================================
class GameController:
    def __init__(self, game_id: str, repository: Optional[GameRepository] = None):
        self.game_id = game_id
        self.board = Board()
        self.turn = Color.WHITE
        self.status = GameStatus.ACTIVE
        self.repo = repository
        self.move_history: List[Move] = []

        if self.repo:
            self.repo.save_game(self.game_id, self.status, self.turn)

    def make_move_by_squares(self, from_str: str, to_str: str) -> bool:
        start_pos = Position.from_algebraic(from_str)
        end_pos = Position.from_algebraic(to_str)

        if self.status != GameStatus.ACTIVE:
            print("Game is over.")
            return False

        piece = self.board.get_piece(start_pos)
        if piece is None or piece.color != self.turn:
            print(f"Invalid move: No {self.turn.value} piece at {from_str}.")
            return False

        if not piece.is_valid_move(end_pos, self.board):
            print(f"Invalid move trajectory for piece at {from_str}.")
            return False

        # Execute move and generate notation record
        move_obj = self.board.move_piece(start_pos, end_pos)
        self.move_history.append(move_obj)

        current_player = self.turn
        
        # Switch turn
        self.turn = Color.BLACK if self.turn == Color.WHITE else Color.WHITE

        # Database Logging
        if self.repo:
            self.repo.log_move(self.game_id, len(self.move_history), current_player, move_obj)
            self.repo.save_game(self.game_id, self.status, self.turn)

        return True

    def print_game_log(self):
        """Displays formatted game log like Chess.com or Lichess"""
        print("\n--- ONLINE GAME LOG ---")
        full_moves = []
        for i in range(0, len(self.move_history), 2):
            move_num = (i // 2) + 1
            white_move = self.move_history[i].notation
            black_move = self.move_history[i + 1].notation if i + 1 < len(self.move_history) else ""
            full_moves.append(f"{move_num}. {white_move:<6} {black_move}")
        
        for move_str in full_moves:
            print(move_str)


# ==========================================
# Demo Execution
# ==========================================
if __name__ == "__main__":
    game = GameController(game_id="game_202")

    game.make_move_by_squares("Nf3", "d5")
    game.make_move_by_squares("g3", "Nf6")
    game.make_move_by_squares("Bg2", "c5")
    game.make_move_by_squares("O-O", "e6")
    game.make_move_by_squares("d3", "Be7")
    game.make_move_by_squares("a4", "O-O")
    game.make_move_by_squares("e4", "Nc6")
    game.make_move_by_squares("Qe2", "dxe4")
    game.make_move_by_squares("dxe4", "e5")
    game.make_move_by_squares("c3", "Be6")
    game.make_move_by_squares("Na3", "Qc7")
    game.make_move_by_squares("Nc4", "Rad8")
    game.make_move_by_squares("Bg5", "h6")
    game.make_move_by_squares("Bxf6", "Bxf6")
    game.make_move_by_squares("Ne3", "Ne7")
    game.make_move_by_squares("h4", "Qc6")
    game.make_move_by_squares("Nd2", "a6")
    game.make_move_by_squares("a5", "Qb5")
    game.make_move_by_squares("Ndc4", "Rd7")
    game.make_move_by_squares("Rfe1", "Rfd8")
    game.make_move_by_squares("Bf1", "Qc6")
    game.make_move_by_squares("Qf3", "Kf8")
    game.make_move_by_squares("Ng4", "Bxg4")
    game.make_move_by_squares("Qxg4", "g6")
    game.make_move_by_squares("h5", "Bg7")
    game.make_move_by_squares("Qf3", "Kg8")
    game.make_move_by_squares("Ne3", "Rd2")
    game.make_move_by_squares("Bc4", "Qf6")
    game.make_move_by_squares("Qxf6", "Bxf6")
    game.make_move_by_squares("hxg6", "Nxg6")
    game.make_move_by_squares("Bd5", "Rxb2")
    game.make_move_by_squares("Reb1", "Rxb1+")
    game.make_move_by_squares("Rxb1", "Ne7")
    game.make_move_by_squares("Bxb7", "Bg5")
    game.make_move_by_squares("Nc4", "Rb8")
    game.make_move_by_squares("Rb6", "Nc8")
    game.make_move_by_squares("Bxc8", "Rxc8")
    game.make_move_by_squares("Rxa6", "Kg7")
    game.make_move_by_squares("Ra7", "Rd8")

    # Display online style game log
    game.print_game_log()