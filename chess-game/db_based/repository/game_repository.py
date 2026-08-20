# ==========================================
# Database Repository for Online Game Logs
# ==========================================
from db_based.models.move import Move
from db_based.models.piece import Color
from db_based.constant.constant import GameStatus
import psycopg2

class GameRepository:
    def __init__(self, db_config: dict):
        self.db_config = db_config

    def _get_connection(self):
        return psycopg2.connect(**self.db_config)

    def save_game(self, game_id: str, status: GameStatus, turn: Color):
        conn = self._get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO games (id, status, current_turn) 
            VALUES (%s, %s, %s)
            ON CONFLICT (id) DO UPDATE 
            SET status = EXCLUDED.status, current_turn = EXCLUDED.current_turn, updated_at = CURRENT_TIMESTAMP;
        """
        cursor.execute(query, (game_id, status.value, turn.value))
        conn.commit()
        cursor.close()
        conn.close()

    def log_move(self, game_id: str, move_num: int, player: Color, move: Move):
        conn = self._get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO moves (game_id, move_number, player, notation, from_square, to_square)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        cursor.execute(query, (
            game_id, 
            move_num, 
            player.value, 
            move.notation, 
            move.start.to_algebraic(), 
            move.end.to_algebraic()
        ))
        conn.commit()
        cursor.close()
        conn.close()

