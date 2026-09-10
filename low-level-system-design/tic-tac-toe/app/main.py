from fastapi import FastAPI
from app.boundary.db import engine
from app.api import router as api_router
from app.models.models import Base

app = FastAPI(title="Template API", version="1.0.0")
app.include_router(api_router)


@app.on_event("startup")
def on_startup():
    import app.models.models  # noqa: F401
    Base.metadata.create_all(bind=engine)

# if __name__ == "__main__":
#     import app.models.models  # noqa: F401
#     SQLModel.metadata.create_all(engine)
#     session = get_session()
#     service = GameService(session=session, winning_strategy=Standard3x3WinningStrategy())

#     # 1. Register Players
#     p1 = service.create_player("Alice", Symbol.X)
#     p2 = service.create_player("Bob", Symbol.O)

#     # 2. Start Game
#     game = service.start_game()
#     print(f"Game Started | ID: {game.id} | Status: {game.status.value}")

#     # 3. Simulate Moves (Alice wins on top row)
#     moves = [
#         (p1, 0, 0),  # Alice X
#         (p2, 1, 0),  # Bob O
#         (p1, 0, 1),  # Alice X
#         (p2, 1, 1),  # Bob O
#         (p1, 0, 2),  # Alice X -> Wins!
#     ]

#     for player, r, c in moves:
#         updated_game = service.play_turn(game.id, player.id, r, c)
#         print(f"Player {player.name} played ({r}, {c}) -> Status: {updated_game.status.value}")

#     if updated_game.winner:
#         print(f"Winner: {updated_game.winner.name}")