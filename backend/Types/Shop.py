class Shop:
    """
    Shop class to store shop data and handle shop operations
    """
    status = "closed"
    sold_items = {}
    buy_items = {}
    prompt = ""
    shopkeeper_description = ""
    shopkeeper_recommendation = ""

    def __init__(self, data: dict = None):
        """
        Initialize shop with data.
        If no data is provided, shop is closed.

        :param data: dict - Optional data to initialize shop
        """
        if isinstance(data, dict) and data != {}:
            self.stock(data)
        else:
            self.close()

    def to_dict(self) -> dict:
        """
        Return shop data as dictionary if it is open, and empty dictionary otherwise.

        :return: shop data
        """
        return {
            "sold_items": self.sold_items,
            "buy_items": self.buy_items,
            "prompt": self.prompt,
            "shopkeeper_description": self.shopkeeper_description,
            "shopkeeper_recommendation": self.shopkeeper_recommendation
        } if self.status == "open" else {}

    def _reset(self, status: str):
        """
        Reset shop data.

        :param status: New status of shop
        """
        self.status = status
        self.sold_items = {}
        self.buy_items = {}
        self.prompt = ""
        self.shopkeeper_description = ""
        self.shopkeeper_recommendation = ""

    def generating(self):
        """
        Set shop status to generating, and clear all data.
        """
        self._reset("generating")

    def close(self):
        """
        Close shop and clear all data.
        """
        self._reset("closed")

    def stock(self, data: dict):
        """
        Open shop with provided data.

        :param data: dict - Generated shop data
        """
        if "problem" in data:  # In case of no available shop in player's location
            self.status = "open"
            self.sold_items = {}
            self.buy_items = {}
            self.prompt = "Foggy weather, can't see anything!"
            self.shopkeeper_description = "No shopkeeper available"
            self.shopkeeper_recommendation = "No available shops at location!"
        else:  # In case of available shop
            self.status = "open"
            self.sold_items = data["sold_items"]
            self.buy_items = data["buy_items"]
            self.prompt = data["prompt"]
            self.shopkeeper_description = data["shopkeeper_description"]
            self.shopkeeper_recommendation = data["shopkeeper_recommendation"]

    def get_sold_item(self, item: str) -> tuple[str, int]:
        """
        Get sold item details from shop.

        :param item: Item name
        :return: Item details, tuple of (category, price)
        """
        if item not in self.sold_items:
            raise ValueError(f"Item {item} not in shop!")
        return self.sold_items[item]

    def get_buy_item(self, item: str) -> tuple[str, int]:
        """
        Get buy item details from shop.

        :param item: Item name
        :return: Item details, tuple of (category, price)
        """
        if item not in self.buy_items:
            raise ValueError(f"Item {item} not wanted!")
        return self.buy_items[item]

    def item_sold(self, item: str):
        """
        Mark item as sold and update shop data.

        :param item: Item name
        """
        category, price = self.sold_items.pop(item)
        self.buy_items[item] = (category, int(price * 0.5))

    def item_bought(self, item: str):
        """
        Mark item as bought and update shop data.

        :param item: Item name
        """
        category, price = self.buy_items.pop(item)
        self.sold_items[item] = (category, int(price * 2))
