from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_invalid_move_returns_400():
    create_response = client.post('/game', json={'player_1': 'Alice', 'player_2': 'Bob'})
    assert create_response.status_code == 200, create_response.text

    game_id = create_response.json()['game_id']
    move_response = client.post(
        f'/game/{game_id}/move',
        json={'player': 999999, 'row': 0, 'col': 0},
    )

    assert move_response.status_code == 400
    assert 'Game or Player not found' in move_response.json()['detail']
