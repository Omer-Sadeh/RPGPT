import json


class Inventory:
    categories = ["weapon", "head", "body", "feet", "neck", "ring", "backpack"]

    def __init__(self, inventory: dict = None, extra_categories: list = None):
        for category in self.categories:
            setattr(self, category, [])

        if inventory:
            for category in list(inventory.keys()):
                self.add_items(inventory[category], category)

        if extra_categories:
            for category in extra_categories:
                self.add_items([], category)

    def to_dict(self):
        return {category: getattr(self, category) for category in self.categories}

    def __dict__(self):
        return self.to_dict()

    def toJSON(self):
        return json.dumps(self.to_dict(), indent=4)

    def __str__(self):
        return str(self.to_dict())

    def __repr__(self):
        return str(self.to_dict())

    def __hash__(self):
        return hash(self.to_dict())

    def __len__(self):
        return sum(len(getattr(self, category)) for category in self.categories)

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __iter__(self):
        return iter(self.categories)

    def __contains__(self, item):
        return item in self.categories

    def __eq__(self, other):
        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        return self.to_dict() != other.to_dict()

    def __add__(self, other):
        for category in other.categories:
            self.add_items(other[category], category)

    def contains(self, item: str, category: str) -> bool:
        if category not in self.categories:
            return False
        return item in getattr(self, category)

    def add_item(self, item: str, category: str):
        if category not in self.categories:
            self.categories.append(category)
            setattr(self, category, [])
        getattr(self, category).append(item)

    def add_items(self, items: list[str], category: str):
        if category not in self.categories:
            self.categories.append(category)
            setattr(self, category, [])
        setattr(self, category, self.__getattribute__(category) + items)

    def remove_item(self, item: str, category: str):
        if category not in self.categories:
            raise ValueError(f"Category {category} not in inventory")
        if item not in getattr(self, category):
            raise ValueError(f"Item {item} not in category {category}")
        getattr(self, category).remove(item)
