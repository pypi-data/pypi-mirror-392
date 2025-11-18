class Market:
    def __init__(self):
        self.items = {
            "apple": 5,
            "bread": 10,
            "protein": 25,
            "energy_drink": 50,
            "wolf": 100,
            "lion": 150,
            "bull": 180,
            "rhinoceros": 250
        }

    def show_items(self):
        print("\n--- MARKET ITEMS ---")
        for item, price in self.items.items():
            print(f"{item}: {price} credits")

    def buy(self, user, item_name):
        if item_name not in self.items:
            print(f"{item_name} not available!")
            return False

        price = self.items[item_name]
        if user.credits < price:
            print("Not enough credits!")
            return False

        user.credits -= price
        user.energy = min(user.energy + 20, 100)  # Alışveriş enerji arttırır
        print(f"{item_name} purchased successfully!")
        return True
