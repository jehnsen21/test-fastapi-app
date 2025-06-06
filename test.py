class Inventory:
    def __init__(self, description: str, qty: str):
        self.description = description
        self.qty = qty

    def get_inventory_details(self):
        return (f"{self.description} - {self.qty} available")

item = Inventory("Logitect mouse", 5)

print(item.get_inventory_details())