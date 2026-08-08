# from flask import Flask, jsonify, request
# from vending_machine import VendingMachine, Item, VendingMachineException

# app = Flask(__name__)
# vm = VendingMachine()

# # Seed Inventory
# vm.inventory.add_item("A1", Item("Coke", 1.50), 5)
# vm.inventory.add_item("B1", Item("Chips", 2.00), 2)

# @app.route('/select', methods=['POST'])
# def select():
#     code = request.json.get('code')
#     try:
#         vm.select_item(code)
#         return jsonify({"status": "Success", "message": f"Selected {code}"}), 200
#     except VendingMachineException as e:
#         return jsonify({"status": "Error", "message": str(e)}), 400

# @app.route('/insert', methods=['POST'])
# def insert():
#     amount = request.json.get('amount', 0.0)
#     try:
#         vm.insert_money(amount)
#         # If state shifted to dispensing automatically inside the loop:
#         if vm.current_state == vm.dispensing_state:
#             item = vm.dispense_item()
#             return jsonify({"status": "Success", "message": f"Dispensed {item.name}"}), 200
#         return jsonify({"status": "Success", "balance": vm.current_balance}), 200
#     except VendingMachineException as e:
#         return jsonify({"status": "Error", "message": str(e)}), 400

# @app.route('/cancel', methods=['POST'])
# def cancel():
#     try:
#         refund = vm.cancel_transaction()
#         return jsonify({"status": "Canceled", "refund": refund}), 200
#     except VendingMachineException as e:
#         return jsonify({"status": "Error", "message": str(e)}), 400

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)