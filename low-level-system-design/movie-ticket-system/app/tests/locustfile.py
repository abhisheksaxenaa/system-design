"""Load test for the movie ticket booking API.

Usage:
    1. Start the API server from the app directory:
       python3 -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
    2. Run Locust:
       locust -f locustfile.py --host http://127.0.0.1:8000
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from locust import HttpUser, between, task


class MovieTicketBookingUser(HttpUser):
    wait_time = between(1, 3)
    host = "http://127.0.0.1:8000"

    def on_start(self) -> None:
        self.movie_id = None
        self.theater_id = None
        self.auditorium_id = None
        self.show_id = None
        self.seat_ids: list[str] = []
        self.booking_id = None

        self._seed_catalog_and_show()

    def _seed_catalog_and_show(self) -> None:
        suffix = uuid4().hex[:8]

        movie_payload = {
            "title": f"Load Test Movie {suffix}",
            "duration_minutes": 150,
            "language": "English",
        }
        movie_response = self.client.post("/movies", json=movie_payload, name="POST /movies")
        movie_response.raise_for_status()
        self.movie_id = movie_response.json()["id"]

        theater_payload = {
            "name": f"Load Test Theater {suffix}",
            "city": "Mumbai",
        }
        theater_response = self.client.post("/theaters", json=theater_payload, name="POST /theaters")
        theater_response.raise_for_status()
        self.theater_id = theater_response.json()["id"]

        auditorium_payload = {"name": f"Auditorium {suffix}"}
        auditorium_response = self.client.post(
            f"/theaters/{self.theater_id}/auditoriums",
            json=auditorium_payload,
            name="POST /theaters/{theater_id}/auditoriums",
        )
        auditorium_response.raise_for_status()
        self.auditorium_id = auditorium_response.json()["id"]

        for row_label in ["A", "B", "C", "D"]:
            for seat_number in range(1, 6):
                seat_response = self.client.post(
                    f"/auditoriums/{self.auditorium_id}/seats",
                    json={
                        "row_label": row_label,
                        "seat_number": seat_number,
                        "category": "REGULAR",
                    },
                    name="POST /auditoriums/{auditorium_id}/seats",
                )
                seat_response.raise_for_status()
                self.seat_ids.append(seat_response.json()["id"])

        starts_at = datetime.now(timezone.utc) + timedelta(days=1)
        show_payload = {
            "movie_id": self.movie_id,
            "auditorium_id": self.auditorium_id,
            "starts_at": starts_at.isoformat(),
            "ends_at": (starts_at + timedelta(minutes=150)).isoformat(),
            "base_price": "199.00",
        }
        show_response = self.client.post("/shows", json=show_payload, name="POST /shows")
        show_response.raise_for_status()
        self.show_id = show_response.json()["id"]

    @task(3)
    def list_shows(self) -> None:
        if self.movie_id is None:
            return
        self.client.get(f"/shows?movie_id={self.movie_id}", name="GET /shows")

    @task(5)
    def view_available_seats(self) -> None:
        if self.show_id is None:
            return
        self.client.get(f"/shows/{self.show_id}/seats", name="GET /shows/{show_id}/seats")

    @task(2)
    def create_booking_hold(self) -> None:
        if self.show_id is None or not self.seat_ids:
            return

        count = min(2, len(self.seat_ids))
        seat_ids = self.seat_ids[:count]
        payload = {"show_id": self.show_id, "seat_ids": seat_ids}
        response = self.client.post(
            "/bookings",
            json=payload,
            headers={"Idempotency-Key": uuid4().hex},
            name="POST /bookings",
        )
        if response.status_code == 201:
            self.booking_id = response.json()["id"]

    @task(1)
    def get_booking(self) -> None:
        if self.booking_id is None:
            return
        self.client.get(f"/bookings/{self.booking_id}", name="GET /bookings/{booking_id}")
