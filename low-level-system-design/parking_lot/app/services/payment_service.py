from typing import Dict

class IPaymentProcessor:
    def process(self, amount: float, details: Dict) -> bool:
        raise NotImplementedError()


class CardPaymentProcessor(IPaymentProcessor):
    def process(self, amount: float, details: Dict) -> bool:
        # Mocked card processing: always succeeds in PoC
        return True


class CashPaymentProcessor(IPaymentProcessor):
    def process(self, amount: float, details: Dict) -> bool:
        # For PoC accept if cash_received >= amount when provided
        received = details.get("cash_received")
        if received is None:
            return True
        return float(received) >= float(amount)


class PaymentService:
    def __init__(self):
        self.card = CardPaymentProcessor()
        self.cash = CashPaymentProcessor()

    def pay(self, method: str, amount: float, details: Dict) -> bool:
        method = method.lower()
        if method == "card":
            return self.card.process(amount, details)
        if method == "cash":
            return self.cash.process(amount, details)
        return False
