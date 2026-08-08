from app.models.item import Item


class InventorySlot:
    def __init__(self, item: Item, quantity: int, max_quantity: int):
        self.item = item
        self.quantity = quantity
        self.max_quantity = max_quantity

    def is_empty(self) -> bool:
        return self.quantity <= 0

    def dispense(self) -> Item:
        if self.is_empty():
            raise ValueError("Cannot dispense from an empty slot.")
        self.quantity -= 1
        return self.item

    def restock(self, quantity: int) -> None:
        if quantity < 0:
            raise ValueError("Cannot restock with a negative quantity.")
        if self.quantity + quantity > self.max_quantity:
            raise ValueError("Cannot restock beyond maximum quantity.")
        self.quantity += quantity

    def get_item_price(self) -> int:
        return self.item.price

class Inventory:
    def __init__(self):
        self.slots: dict[str, InventorySlot] = {}
    
    def add_slot(self, code: str, item: Item, quantity: int, max_quantity: int) -> None:
        if code in self.slots:
            raise ValueError(f"Slot with code {code} already exists.")
        self.slots[code] = InventorySlot(item, quantity, max_quantity)

    def get_slot(self, code: str) -> InventorySlot:
        if code not in self.slots:
            raise ValueError(f"No slot found for code {code}.")
        return self.slots[code]

    def is_item_available(self, code: str) -> bool:
        slot = self.get_slot(code)
        return not slot.is_empty()

    def dispense_item(self, code: str) -> Item:
        slot = self.get_slot(code)
        return slot.dispense()

    def restock_item(self, code: str, quantity: int) -> None:
        slot = self.get_slot(code)
        slot.restock(quantity)