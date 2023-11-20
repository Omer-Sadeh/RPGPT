class Inventory:
    categories = ["weapon", "head", "body", "feet", "neck", "ring", "backpack"]
    
    def __init__(self, inventory: dict = None, extra_categories: list[str] = []):
        for category in self.categories:
            setattr(self, category, [])
        for category in extra_categories:
            if category not in self.categories:
                setattr(self, category, [])
                self.categories.append(category)
        if inventory:
            for category in list(inventory.keys()):
                if category not in self.categories:
                    self.categories.append(category)
                setattr(self, category, inventory[category])
                if category not in self.categories:
                    self.categories.append(category)
    
    def to_dict(self):
        return {category: getattr(self, category) for category in self.categories}
    
    def __str__(self):
        return str(self.to_dict())
    
    def __repr__(self):
        return str(self.to_dict())
    
    def __hash__(self):
        return hash(str(self.to_dict()))
    
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
        temp1 = self.to_dict()
        temp2 = other.to_dict()
        for category in list(temp2.keys()):
            if category not in temp1:
                temp1[category] = []
            for item in temp2[category]:
                if item not in temp1[category]:
                    temp1[category].append(item)
        return Inventory(temp1)
    
    def contains(self, item: str, category: str) -> bool:
        if category not in self.categories:
            return False
        return item in getattr(self, category)
    
    def add_item(self, item: str, category: str):
        if category not in self.categories:
            self.categories.append(category)
            setattr(self, category, [])
        getattr(self, category).append(item)
        
    def remove_item(self, item: str, category: str):
        if category not in self.categories:
            raise ValueError(f"Category {category} not in inventory")
        if item not in getattr(self, category):
            raise ValueError(f"Item {item} not in category {category}")
        getattr(self, category).remove(item)
    
class Theme:
    def __init__(self, name: str, fields: dict = None, skills: list[str] = [], extra_inventory_categories: list[dict] = None, extra_fields: list[dict] = None):
        self.name: str = name
        self.fields: dict = {"gender": ["Male", "Female",  "Other"]}
        self.extra_inventory_categories: list[dict] = extra_inventory_categories or []
        self.extra_fields: list[dict] = extra_fields or []
        if skills != [] and len(skills) < 3:
            raise ValueError(f"Theme {name} must have at least 3 skills!")
        self.skills: list[str] = skills if skills else ["INT", "STR", "AGL", "LUCK", "CHR", "PER"]
        if fields:
            for field in list(fields.keys()):
                self.fields[field] = fields[field]
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name
    
    def __hash__(self):
        return hash(self.name)
    
    def __len__(self):
        return len(self.name)
    
    def __eq__(self, other):
        return self.name == other.name
    
    def __ne__(self, other):
        return self.name != other.name
    
    def get_fields(self) -> list[str]:
        return list(self.fields.keys())
    
    def get_field_options(self, field: str) -> list[str]:
        return self.fields[field]
    
    def generate_empty_inventory(self, fields_choices: dict) -> Inventory:
        extra_categories = set()
        for category in self.extra_inventory_categories:
            if category["value"] == "ALL" or fields_choices[category["field"]] in category["value"]:
                extra_categories.update(category["categories"])
        return Inventory(extra_categories=list(extra_categories))
    