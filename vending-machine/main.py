# Create a main class to test Vending Machine with below cases:
# 1. Create a vending machine with 3 slots and add items to it.
# 2. Select an item and insert money to buy it.
# 3. Try to select an item that is out of stock.
# 4. Try to insert money without selecting an item.
# 5. Try to dispense an item without inserting enough money.
# 6. Try to cancel a transaction after selecting an item and inserting money.
# 7. Try to do race condition where a concurrent transaction tries to select the same item and insert money at the same time.
from app.models.inventory import Inventory
from app.models.item import Item
from app.vending_machine import VendingMachine

def start_test_case(case: str, description: str = ""):
    print(f"\n--- Test Case Start: {case} ---\n")
    if description:
        print(f"Description: {description}\n")

def end_test_case(case: str):
    print(f"\n--- Test Case End: {case} ---\n")

def main():
    # Create items
    item1 = Item(name="Soda", price=150)
    item2 = Item(name="Chips", price=100)
    item3 = Item(name="Candy", price=50)

    # Create inventory and add slots
    inventory = Inventory()
    inventory.add_slot(code="A1", item=item1, quantity=5, max_quantity=10)
    inventory.add_slot(code="B1", item=item2, quantity=0, max_quantity=10)  # Out of stock
    inventory.add_slot(code="C1", item=item3, quantity=3, max_quantity=10)

    # Create vending machine
    vending_machine = VendingMachine(inventory)

    # Test case 1: Select an item and insert money to buy it.
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
    start_test_case("2", "Try to select an item that is out of stock.")
    try:
        vending_machine.select_item("B1")
    except Exception as e:
        print(e)
    finally:
        end_test_case("2")

    # Test case 3: Try to insert money without selecting an item.
    start_test_case("3", "Try to insert money without selecting an item.")
    try:
        vending_machine.insert_money(100)
    except Exception as e:
        print(e)
    finally:
        end_test_case("3")

    # Test case 4: Try to dispense an item without inserting enough money.
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

if __name__ == "__main__":
    main()