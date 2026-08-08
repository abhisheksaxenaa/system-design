import abc
from typing import Optional

from app.models.item import Item
from app.vending_machine import VendingMachine

class VendingMachineException(Exception):
    pass

class VendingMachineState(abc.ABC):
    @abc.abstractmethod
    def select_item(self, machine: VendingMachine, code: str) -> None:
        pass

    @abc.abstractmethod
    def insert_money(self, machine: VendingMachine, amount: float) -> None:
        pass

    @abc.abstractmethod
    def dispense_item(self, machine: VendingMachine) -> Optional[Item]:
        pass

    @abc.abstractmethod
    def cancel_transaction(self, machine: VendingMachine) -> float:
        pass

class IdleState(VendingMachineState):
    def select_item(self, machine: VendingMachine, code: str) -> None:
        if not machine.inventory.is_item_available(code):
            raise VendingMachineException(f"Item {code} is out of stock.")
        
        machine.current_selected_code = code
        machine.set_state(machine.has_item_selection_state)
        print(f"Item {code} selected. Price: ${machine.inventory.get_slot(code).get_item_price()}")

    def insert_money(self, machine: VendingMachine, amount: float) -> None:
        raise VendingMachineException("Please select an item first.")

    def dispense_item(self, machine: VendingMachine) -> Optional[Item]:
        raise VendingMachineException("No item selected.")

    def cancel_transaction(self, machine: VendingMachine) -> float:
        raise VendingMachineException("No active transaction to cancel.")

class HasItemSelectionState(VendingMachineState):
    def select_item(self, machine: VendingMachine, code: str) -> None:
        raise VendingMachineException("Item already selected. Please insert money or cancel.")

    def insert_money(self, machine: VendingMachine, amount: float) -> None:
        if amount <= 0:
            raise VendingMachineException("Inserted amount must be positive.")
        
        machine.current_balance += amount
        item_price = machine.inventory.get_slot(machine.current_selected_code).get_item_price()
        
        if machine.current_balance >= item_price:
            machine.set_state(machine.dispensing_state)
            print(f"Enough money inserted. Dispensing item {machine.current_selected_code}.")
        else:
            print(f"Inserted ${amount}. Current balance: ${machine.current_balance}. Item price: ${item_price}.")

    def dispense_item(self, machine: VendingMachine) -> Optional[Item]:
        raise VendingMachineException("Please insert enough money to dispense the item.")

    def cancel_transaction(self, machine: VendingMachine) -> float:
        refund = machine.current_balance
        machine.current_balance = 0
        machine.reset_selected_code()
        machine.set_state(machine.idle_state)
        print(f"Transaction canceled. Refunded ${refund}.")
        return refund

class DispensingState(VendingMachineState):
    def select_item(self, machine: VendingMachine, code: str) -> None:
        raise VendingMachineException("Currently dispensing an item. Please wait.")

    def insert_money(self, machine: VendingMachine, amount: float) -> None:
        raise VendingMachineException("Currently dispensing an item. Cannot accept more money.")

    def dispense_item(self, machine: VendingMachine) -> Optional[Item]:
        slot = machine.inventory.get_slot(machine.current_selected_code)
        if slot.is_empty():
            raise VendingMachineException(f"Item {machine.current_selected_code} is out of stock.")
        
        dispensed_item = slot.dispense_item()
        machine.current_balance -= dispensed_item.price
        print(f"Dispensed {dispensed_item.name}. Remaining balance: ${machine.current_balance}.")
        
        # Reset for next transaction
        machine.reset_selected_code()
        machine.set_state(machine.idle_state)
        return dispensed_item

    def cancel_transaction(self, machine: VendingMachine) -> float:
        raise VendingMachineException("Cannot cancel transaction while dispensing an item.")