from threading import Lock
from typing import Optional

from app.models.inventory import Inventory
from app.models.item import Item
from app.state.vending_machine_state import DispensingState, HasItemSelectionState, IdleState, VendingMachineState


class VendingMachine:
    def __init__(self, inventory: Inventory):
        self.inventory = inventory
        self._lock = Lock()

        # Initialize States
        self.idle_state = IdleState()
        self.has_item_selection_state = HasItemSelectionState()
        self.dispensing_state = DispensingState()

        # Initial State Configuration
        self.state: VendingMachineState = self.idle_state
        self.current_selected_code: Optional[str] = None
        self.current_balance: int = 0


    def set_state(self, state: VendingMachineState) -> None:
        self.state = state

    # TODO: Method to reset current balance

    # TODO: Method to reset current selected code
    def reset_selected_code(self) -> None:
        self.current_selected_code = None

    def select_item(self, code: str) -> None:
        with self._lock:
            self.state.select_item(self, code)

    def insert_money(self, amount: float) -> None:
        with self._lock:
            self.state.insert_money(self, amount)

    def dispense_item(self) -> Optional[Item]:
        with self._lock:
            return self.state.dispense_item(self)

    def cancel_transaction(self) -> float:
        with self._lock:
            return self.state.cancel_transaction(self)