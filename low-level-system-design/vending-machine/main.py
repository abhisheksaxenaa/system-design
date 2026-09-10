# Create a main class to test Vending Machine with below cases:
# 1. Create a vending machine with 3 slots and add items to it.
# 2. Select an item and insert money to buy it.
# 3. Try to select an item that is out of stock.
# 4. Try to insert money without selecting an item.
# 5. Try to dispense an item without inserting enough money.
# 6. Try to cancel a transaction after selecting an item and inserting money.
# 7. Try to do race condition where a concurrent transaction tries to select the same item and insert money at the same time.
import threading
import time

from app.models.inventory import Inventory
from app.models.item import Item
from app.vending_machine import VendingMachine

def start_test_case(case: str, description: str = ""):
    print(f"\n--- Test Case Start: {case} ---\n")
    if description:
        print(f"Description: {description}\n")

def end_test_case(case: str):
    print(f"--- Test Case End: {case} ---\n")


def create_vending_machine() -> VendingMachine:
    item1 = Item(name="Soda", price=150)
    item2 = Item(name="Chips", price=100)
    item3 = Item(name="Candy", price=50)

    inventory = Inventory()
    inventory.add_slot(code="A1", item=item1, quantity=5, max_quantity=10)
    inventory.add_slot(code="B1", item=item2, quantity=0, max_quantity=10)
    inventory.add_slot(code="C1", item=item3, quantity=3, max_quantity=10)

    return VendingMachine(inventory)


def perform_transaction(name: str, machine: VendingMachine, code: str, amount: int):
    try:
        machine.select_item(code)
        time.sleep(0.1)
        machine.insert_money(amount)
        dispensed_item = machine.dispense_item()
        print(f"{name}: Dispensed {dispensed_item.name}")
    except Exception as e:
        print(f"{name}: {e}")


def main():
    # Test case 1: Select an item and insert money to buy it.
    vending_machine = create_vending_machine()
    start_test_case("1", "Select an item and insert money to buy it.")
    try:
        vending_machine.select_item("A1")
        vending_machine.insert_money(200)  # Insert more than the price
        dispensed_item = vending_machine.dispense_item()
        print(f"Dispensed: {dispensed_item.name}")
    except Exception as e:
        print(e)
    finally:
        end_test_case("1")

    # Test case 2: Try to select an item that is out of stock.
    vending_machine = create_vending_machine()
    start_test_case("2", "Try to select an item that is out of stock.")
    try:
        vending_machine.select_item("B1")
    except Exception as e:
        print(e)
    finally:
        end_test_case("2")

    # Test case 3: Try to insert money without selecting an item.
    vending_machine = create_vending_machine()
    start_test_case("3", "Try to insert money without selecting an item.")
    try:
        vending_machine.insert_money(100)
    except Exception as e:
        print(e)
    finally:
        end_test_case("3")

    # Test case 4: Try to dispense an item without inserting enough money.
    vending_machine = create_vending_machine()
    start_test_case("4", "Try to dispense an item without inserting enough money.")
    try:
        vending_machine.select_item("C1")
        vending_machine.insert_money(30)  # Not enough money
        vending_machine.dispense_item()
    except Exception as e:
        print(e)
    finally:
        end_test_case("4")

    # Test case 5: Try to cancel a transaction after selecting an item and inserting money.
    vending_machine = create_vending_machine()
    start_test_case("5", "Try to cancel a transaction after selecting an item and inserting money.")
    try:
        vending_machine.select_item("C1")
        vending_machine.insert_money(50)
        refunded_amount = vending_machine.cancel_transaction()
        print(f"Transaction cancelled. Refunded amount: ${refunded_amount}")
    except Exception as e:
        print(e)
    finally:
        end_test_case("5")

    # Test case 6: Cancel a transaction after selecting an item and inserting money.
    vending_machine = create_vending_machine()
    start_test_case("6", "Cancel a transaction after selecting an item and inserting money.")
    try:
        vending_machine.select_item("C1")
        vending_machine.insert_money(50)
        refunded_amount = vending_machine.cancel_transaction()
        print(f"Transaction cancelled. Refunded amount: ${refunded_amount}")
    except Exception as e:
        print(e)
    finally:
        end_test_case("6")

    # Test case 7: Race condition where two concurrent transactions try the same item.
    vending_machine = create_vending_machine()
    start_test_case("7", "Try a race condition with two concurrent transactions selecting the same item.")
    thread1 = threading.Thread(target=perform_transaction, args=("Thread-1", vending_machine, "A1", 150))
    thread2 = threading.Thread(target=perform_transaction, args=("Thread-2", vending_machine, "A1", 150))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()
    end_test_case("7")

if __name__ == "__main__":
    main()
