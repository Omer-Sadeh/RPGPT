class Shop:
    status = "closed"
    sold_items = {}
    buy_items = {}
    prompt = ""
    shopkeeper_recommendation = ""

    def __init__(self, data: dict = None):
        if isinstance(data, dict) and data != {}:
            self.stock(data)
        else:
            self.close()

    def to_dict(self) -> dict | str:
        return {
            "sold_items": self.sold_items,
            "buy_items": self.buy_items,
            "prompt": self.prompt,
            "shopkeeper_recommendation": self.shopkeeper_recommendation
        } if self.status == "open" else {}

    def generating(self):
        self.status = "generating"
        self.sold_items = {}
        self.buy_items = {}
        self.prompt = ""
        self.shopkeeper_recommendation = ""

    def close(self):
        self.status = "closed"
        self.sold_items = {}
        self.buy_items = {}
        self.prompt = ""
        self.shopkeeper_recommendation = ""

    def stock(self, data: dict):
        self.status = "open"
        self.sold_items = data["sold_items"]
        self.buy_items = data["buy_items"]
        self.prompt = data["prompt"]
        self.shopkeeper_recommendation = data["shopkeeper_recommendation"]

    def get_sold_item(self, item: str) -> tuple:
        if item not in self.sold_items:
            raise ValueError(f"Item {item} not in shop!")
        return self.sold_items[item]

    def get_buy_item(self, item: str) -> tuple:
        if item not in self.buy_items:
            raise ValueError(f"Item {item} not wanted!")
        return self.buy_items[item]

    def item_sold(self, item: str):
        category, price = self.sold_items.pop(item)
        self.buy_items[item] = (category, int(price * 0.5))

    def item_bought(self, item: str):
        category, price = self.buy_items.pop(item)
        self.sold_items[item] = (category, int(price * 2))
