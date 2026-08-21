from app.main import app


def test_openapi_includes_game_endpoints():
    schema = app.openapi()
    paths = schema.get('paths', {})

    assert '/game' in paths
    assert '/game/{game_id}/move' in paths
