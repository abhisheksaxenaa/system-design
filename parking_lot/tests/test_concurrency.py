from fastapi.testclient import TestClient
from datetime import datetime
from app.main import app
from app.db import engine
from sqlmodel import SQLModel, Session
from app.models.models import Spot
from sqlalchemy import update
import concurrent.futures


client = TestClient(app)


def setup_module(module):
    # ensure tables exist
    SQLModel.metadata.create_all(engine)


def test_concurrent_allocation():
    # Occupy any existing spots, then create exactly one free spot for the test
    # with Session(engine) as s:
    #     s.exec(update(Spot).values(is_free=False))
    #     s.commit()

    def take_ticket(license_plate: str):
        return client.post("/entry/ticket", json={"license_plate": license_plate, "vehicle_type": "motorcycle"})

    # Run two requests concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        f1 = ex.submit(take_ticket, f"UP13BY{int(datetime.timestamp(datetime.now()) % 10000)}")
        f2 = ex.submit(take_ticket, f"UP12BA{int(datetime.timestamp(datetime.now()) % 10000)}")
        r1 = f1.result()
        r2 = f2.result()

    statuses = sorted([r1.status_code, r2.status_code])
    # Expect one success (200) and one conflict (409)
    assert statuses == [200, 409]
