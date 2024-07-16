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
    """
    Class to store the save data of a player.
    Handles the story, shop, goals, memories, theme, background, level, experience points, action points, skills,
    inventory, coins, and death status of the player.
    Also, handles all the operations related to the save data.
    """
    def __init__(self, data: dict = None, theme: str = None, background: dict = None,
                 inventory: dict | Inventory = None):
        """
        Initializes the SaveData object with the provided data.
        If data is not provided, theme and background must be provided to create a new save.
        """
        if data:  # create from existing data
            self.set_from_dict(data)
        else:  # create new save
            if not theme or not background:
                raise ValueError("Theme and background must be provided if data is not provided.")

            # get the Theme object from the theme name
            generated_theme = Themes.get_theme(theme)

            # generate the data's inventory
            if not inventory:
                generated_inventory = generated_theme.generate_empty_inventory(background)
            elif isinstance(inventory, dict):
                generated_inventory = Inventory(inventory)
            elif isinstance(inventory, Inventory):
                generated_inventory = inventory
            else:
                raise ValueError("Inventory must be a dictionary or an Inventory object.")

            # initialize the SaveData object with the generated data
            self.story = {}
            self.shop = Shop()
            self.goals = []
            self.memories = []
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
        """
        Sets the SaveData object from the provided dictionary.

        :param data: the dictionary to set the SaveData object from
        """
        self.story = data["story"]
        self.shop = Shop(data["shop"])
        self.goals = data["goals"]
        self.memories = data["memories"]
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

    def to_dict(self) -> dict:
        """
        Converts the SaveData object to a dictionary.

        :return: the dictionary representation of the SaveData object
        """
        return {
            "story": self.story,
            "shop": self.shop.to_dict(),
            "goals": self.goals,
            "memories": self.memories,
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

    def __str__(self):
        return f"SaveData(theme={self.theme}, background={self.background}, level={self.level}, xp={self.xp}, " \
               f"xp_to_next_level={self.xp_to_next_level}, action_points={self.action_points}, skills={self.skills}, " \
               f"inventory={self.inventory}, coins={self.coins}, death={self.death})"

    def __repr__(self):
        return self.__str__()

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
        """
        Advances the version of the save data.
        Used for change synchronization, mainly for multi-threading in caching.
        """
        self.ver += 1

    def init_story(self, goal: dict = None):
        """
        Initializes the story of the player.
        Includes setting the history, scene, prompt, image, status, goal, health, options, rates, advantages, levels,
        and experience points.

        :param goal: the goal to be set for the player - Optional
        """
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
            "experience": [0, 0, 0]
        }
        if goal:
            self.story["goal_status"] = "in progress"
            self.story["gold_reward"] = goal["gold_reward"]
            self.story["xp_reward"] = goal["xp_reward"]
        self.shop.close()
        self.goals = []

    def update_story(self, result: dict, action: str):
        """
        Updates the story of the player based on the result of an action.

        :param result: the result of the action
        :param action: the action taken by the player
        """
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
            self.story["advantages"] = [skill if skill in list(self.skills.keys()) else list(self.skills.keys())[0] for skill in result["advantages"]]
            self.story["levels"] = result["level"]
            self.story["experience"] = result["experience"]
        else:
            self.story["options"] = []
        if self.story["goal"]:
            self.story["goal_status"] = result["goal_status"]
        if "new_location" in result:
            self.background["location"] = result["new_location"]
        self.add_xp(result_xp)
        self.story["status"] = result["action_result"]
        self.shop.close()

    def add_xp(self, xp: int):
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

    def goals_list(self) -> list[str]:
        """
        Returns the list of goals of the player.

        :return: the list of goals of the player
        """
        return [goal["goal"] for goal in self.goals]
