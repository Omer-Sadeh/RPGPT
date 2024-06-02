from backend.Types.Inventory import Inventory


class Theme:
    """
    A class to represent a Theme in the game.
    """

    def __init__(self, name: str, fields: dict = None, skills=None, extra_inventory_categories: list[dict] = None,
                 extra_fields: list[dict] = None):
        """
        Constructor for the Theme class.

        :param name: str: The name of the Theme.
        :param fields: dict: The fields of the Theme, Optional.
        :param skills: list[str]: The skills of the Theme, Optional.
        :param extra_inventory_categories: list[dict]: The extra inventory categories of the Theme, Optional.
        :param extra_fields: list[dict]: The extra fields of the Theme, Optional.
        """
        if skills is None:
            skills = []
        self.name: str = name
        self.fields: dict = {"gender": ["Male", "Female",  "Other"], "details": "freetext"}
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

    def todict(self) -> dict:
        """
        Convert the Theme to a dictionary.

        :return: dict: The Theme as a dictionary.
        """
        return {
            "name": self.name,
            "fields": self.fields,
            "skills": self.skills,
            "extra_inventory_categories": self.extra_inventory_categories,
            "extra_fields": self.extra_fields
        }

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

    def get_generated_extra_fields(self, fields_choices: dict) -> list[dict]:
        """
        Returns the extra fields that are AI-generated based on the choices of the fields.

        :param fields_choices: The choices of the fields, given as the background.
        """
        extra_fields = []
        for extra_field in self.extra_fields:
            if fields_choices[extra_field["field"]] in extra_field["value"]:
                if isinstance(extra_field["extra_field_value"], str) and extra_field["extra_field_value"] != "freetext":
                    extra_fields.append(extra_field)
        return extra_fields

    def get_required_extra_fields(self, fields_choices: dict) -> list[str]:
        """
        Returns the extra fields that are required from the player based on the choices of the fields.

        :param fields_choices: The choices of the fields, given as the background.
        """
        extra_fields = []
        for extra_field in self.extra_fields:
            if fields_choices[extra_field["field"]] in extra_field["value"]:
                if isinstance(extra_field["extra_field_value"], str) and extra_field["extra_field_value"] == "freetext":
                    extra_fields.append(extra_field["extra_field"])
        return extra_fields

    def get_all_required_fields(self, fields_choices: dict) -> list[str]:
        """
        Returns all the required fields for the Theme.

        :param fields_choices: The choices of the fields, given as the background.
        """
        return list(self.fields.keys()) + self.get_required_extra_fields(fields_choices)

    def generate_empty_inventory(self, fields_choices: dict) -> Inventory:
        """
        Generates an empty inventory for the Theme, containing the extra categories based on the choices of the fields.

        :param fields_choices: The choices of the fields, given as the background.
        """
        extra_categories = set()
        for category in self.extra_inventory_categories:
            if category["value"] == "ALL" or fields_choices[category["field"]] in category["value"]:
                extra_categories.update(category["categories"])
        return Inventory(extra_categories=list(extra_categories))
