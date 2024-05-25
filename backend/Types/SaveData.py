import json
from backend.Types import Themes
from backend.Types.Inventory import Inventory
from backend.Types.Shop import Shop


def remove_init_num(input_string: str) -> str:
    """
    Removes the initial number from a string if it exists.
    Used in parsing the options from the story.

    :param input_string: the string to be parsed
    :return: the string without the initial number
    """
    if len(input_string) > 2 and input_string[0].isdigit() and input_string[1] == '.' and input_string[2] == ' ':
        return input_string[3:]
    else:
        return input_string


class SaveData:
    def __init__(self, data: dict = None, theme: str = None, background: dict = None, inventory: dict | Inventory = None):
        if data:  # create from existing data
            self.set_from_dict(data)
        else:  # create new save
            if not theme or not background:
                raise ValueError("Theme and background must be provided if data is not provided.")

            generated_theme = Themes.get_theme(theme)
            if not inventory:
                generated_inventory = generated_theme.generate_empty_inventory(background)
            elif isinstance(inventory, dict):
                generated_inventory = Inventory(inventory)
            elif isinstance(inventory, Inventory):
                generated_inventory = inventory
            else:
                raise ValueError("Inventory must be a dictionary or an Inventory object.")

            self.story = {}
            self.shop = Shop()
            self.goals = []
            self.theme = generated_theme
            self.background = background
            self.level = 1
            self.xp = 0
            self.xp_to_next_level = 75
            self.action_points = 0
            self.skills = {skill: 1 for skill in generated_theme.skills}
            self.inventory = generated_inventory
            self.coins = 100
            self.death = False
            self.ver = 0

    def set_from_dict(self, data: dict):
        self.story = data["story"]
        self.shop = Shop(data["shop"])
        self.goals = data["goals"]
        self.theme = Themes.get_theme(data["theme"]) if isinstance(data["theme"], str) else data["theme"]
        self.background = data["background"]
        self.level = data["level"]
        self.xp = data["xp"]
        self.xp_to_next_level = data["xp_to_next_level"]
        self.action_points = data["action_points"]
        self.skills = data["skills"]
        self.inventory = Inventory(inventory=data["inventory"]) if isinstance(data["inventory"], dict) else data["inventory"]
        self.coins = data["coins"]
        self.death = data["death"]
        self.ver = data["ver"]

    def __str__(self):
        return f"SaveData(theme={self.theme}, background={self.background}, level={self.level}, xp={self.xp}, " \
               f"xp_to_next_level={self.xp_to_next_level}, action_points={self.action_points}, skills={self.skills}, " \
               f"inventory={self.inventory}, coins={self.coins}, death={self.death})"

    def __repr__(self):
        return self.__str__()

    def to_dict(self) -> dict:
        return {
            "story": self.story,
            "shop": self.shop.to_dict(),
            "goals": self.goals,
            "theme": str(self.theme),
            "background": self.background,
            "level": self.level,
            "xp": self.xp,
            "xp_to_next_level": self.xp_to_next_level,
            "action_points": self.action_points,
            "skills": self.skills,
            "inventory": self.inventory.to_dict(),
            "coins": self.coins,
            "death": self.death,
            "ver": self.ver
        }

    def __dict__(self):
        return self.to_dict()

    def toJSON(self):
        return json.dumps(self.to_dict(), indent=4)

    def __hash__(self):
        return hash(self.to_dict())

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __eq__(self, other):
        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        return self.to_dict() != other.to_dict()

    def advance_version(self):
        self.ver += 1

    def init_story(self, goal: dict = None):
        skills = list(self.skills.keys())
        self.story = {
            "history": [],
            "scene": "",
            "prompt": "",
            "img": "",
            "status": "",
            "goal": goal["goal"] if goal else "",
            "health": 5,
            "options": ["Wake up", "Look around", "Stand up"],
            "rates": [1, 1, 1],
            "advantages": [skills[0], skills[1], skills[2]],
            "levels": [0, 0, 0],
            "experience": [0, 0, 0],
            "cache": {}
        }
        if goal:
            self.story["goal_status"] = "in progress"
            self.story["gold_reward"] = goal["gold_reward"]
            self.story["xp_reward"] = goal["xp_reward"]
        self.shop.close()
        self.goals = []

    def update_story(self, result: dict, action: str):
        self.story["history"] += [action + ".", result["scene"]]
        action_index = self.story["options"].index(action)
        result_xp = 0 if result["action_result"] == "Failure" else self.story["experience"][action_index]
        self.story["health"] = result["health"]
        self.inventory = Inventory(result["inventory"])
        self.coins = result["coins"]
        self.story["scene"] = result["scene"]
        self.story["prompt"] = result["prompt"]
        if "options" in result:
            self.story["options"] = [remove_init_num(option) for option in result["options"] if option != ""]
            self.story["rates"] = result["rates"]
            self.story["advantages"] = [skill if skill in list(self.skills.keys()) else "INT" for skill in result["advantages"]]
            self.story["levels"] = result["level"]
            self.story["experience"] = result["experience"]
        else:
            self.story["options"] = []
        if self.story["goal"]:
            self.story["goal_status"] = result["goal_status"]
        if "new_backstory" in result:
            self.story["new_backstory"] = result["new_backstory"]
        self.story["cache"] = {}
        self.add_xp(result_xp)
        self.story["status"] = result["action_result"]

    def add_xp(self, xp: int) -> None:
        """
        Updates the experience points of the player based on the added experience points.
        Includes updating the level, experience points, and action points.

        :param xp: the experience points to be added to the player
        """
        current_xp = self.xp + xp

        while current_xp >= self.xp_to_next_level:
            current_xp -= self.xp_to_next_level
            self.level += 1
            self.xp_to_next_level = 25 * ((self.level + 2) ** 2) - 50 * (self.level + 2)
            self.action_points += 1

        self.xp = current_xp

    def goals_list(self):
        return [goal["goal"] for goal in self.goals]
