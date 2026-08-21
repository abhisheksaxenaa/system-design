
from sqlalchemy.orm import Session

from app.repos.winning_strategy import WinningStrategy
from app.models.models import PlayerModel, GameModel, MoveModel, Symbol, GameState
from app.repos.winning_strategy import Board

class GameService:
    def __init__(self, session: Session, winning_strategy: WinningStrategy):
        self.session = session
        self.winning_strategy = winning_strategy

    def create_player(self, name: str, symbol: Symbol) -> PlayerModel:
        player = PlayerModel(name=name, symbol=symbol)
        self.session.add(player)
        self.session.commit()
        return player

    def start_game(self) -> GameModel:
        initial_board = Board()
        game = GameModel(
            status=GameState.IN_PROGRESS,
            board_state=initial_board.to_json()
        )
        self.session.add(game)
        self.session.commit()
        return game

    def play_turn(self, game_id: int, player_id: int, row: int, col: int) -> GameModel:
        game = self.session.query(GameModel).filter_by(id=game_id).first()
        player = self.session.query(PlayerModel).filter_by(id=player_id).first()

        if not game or not player:
            raise ValueError("Game or Player not found.")
        if game.status != GameState.IN_PROGRESS:
            raise ValueError("Game is already finished.")

        board = Board.from_json(game.board_state)

        if not board.make_move(row, col, player.symbol):
            raise ValueError("Invalid move. Cell occupied or out of bounds.")

        # Record Move
        move = MoveModel(game_id=game.id, player_id=player.id, row=row, col=col)
        self.session.add(move)

        # Check Game State
        if self.winning_strategy.check_winner(board.grid, row, col, player.symbol):
            game.status = GameState.FINISHED
            game.winner = player
        elif board.is_full():
            game.status = GameState.DRAW

        game.board_state = board.to_json()
        self.session.commit()
        return game