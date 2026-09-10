from fastapi.testclient import TestClient
from app.main import app
from app.db import engine
from sqlmodel import SQLModel


client = TestClient(app)


def setup_module(module):
    import app.models.models as models
    SQLModel.metadata.create_all(engine)


def test_full_flow_entry_pay_exit():
    # create a spot as admin
    headers = {"X-API-KEY": "admin-token"}
    resp = client.post("/admin/spots", json={"floor": 1, "spot_type": "compact"}, headers=headers)
    assert resp.status_code == 200
    spot = resp.json()

    # take ticket
    resp = client.post("/entry/ticket", json={"license_plate": "ABC123", "vehicle_type": "car"})
    assert resp.status_code == 200
    ticket = resp.json()

    ticket_id = ticket["ticket_id"]

    # scan ticket
    resp = client.get(f"/ticket/{ticket_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert "estimated_fee" in data

    # pay ticket (card)
    resp = client.post(f"/ticket/{ticket_id}/pay", json={"method": "card", "details": {}})
    assert resp.status_code == 200

    # exit parking
    resp = client.post(f"/exit/{ticket_id}")
    assert resp.status_code == 200
