from locust import HttpUser, task

RTO_CODE = [
    "AP", "AR", "AS", "BR", "CG", "CH", "DD", "DL", "DN", "GA",
    "GJ", "HR", "HP", "JH", "JK", "KA", "KL", "LA", "LD", "MH", "ML", "MN",
    "MP", "MZ", "NL", "OD", "PB", "PY", "RJ", "SK", "TN", "TS", "TR", "UK", "UP", "WB"
]

class ParkingLotUser(HttpUser):
    @task
    def allocate_ticket(self):
        # license_plate: str, vehicle_type: car|truck|motorcycle
        # Randomize license plate and vehicle type for testing
        # License plate format: <RTO_CODE><2 digit number less than 20><2 uppercase letters><4 digit number>
        request_count = getattr(self.environment.runner.stats, "num_requests", None)
        if request_count is None:
            request_count = getattr(self.environment.runner.stats, "total_requests", 0)
        request_count = int(request_count or 0)

        license_plate = f"{RTO_CODE[request_count % len(RTO_CODE)]}{request_count % 20:02d}{chr(65 + request_count % 26)}{chr(65 + (request_count // 26) % 26)}{request_count % 10000:04d}"
        vehicle_type = ["car", "truck", "motorcycle"][request_count % 3]
        self.client.post("/entry/ticket", json={
            "license_plate": license_plate,
            "vehicle_type": vehicle_type
        })

    @task
    def checkout_ticket(self):
        # Randomly select a ticket_id to checkout
        # Get ticket details first to compute fee and then pay
        # payment type can be card or cash, randomly selected
        # ticket_id range is assumed to be from 1 to 200 for testing purposes
        # ticket_response.json() will have ticket_id, estimated_fee
        # use estimated fees to pay the ticket
        ticket_id = (getattr(self.environment.runner.stats, "num_requests", 0) % 1000) + 1
        ticket_response = self.client.get(f"/ticket/{ticket_id}")
        ticket_data = ticket_response.json()
        # If ticket is not found, skip payment and exit
        if "detail" in ticket_data and ticket_data["detail"] == "Ticket not found":
            return
        payment_type = ["card", "cash"][getattr(self.environment.runner.stats, "num_requests", 0) % 2]
        pay_ticket_response = self.client.post(f"/ticket/{ticket_id}/pay", json={
            "method": payment_type,
            "details": {"cash_received": ticket_data["estimated_fee"]}
        })
        pay_ticket_data = pay_ticket_response.json()
        if "detail" in pay_ticket_data and pay_ticket_data["detail"] == "Ticket already paid":
            return
        # now exit the parking lot
        self.client.post(f"/exit/{ticket_id}")
