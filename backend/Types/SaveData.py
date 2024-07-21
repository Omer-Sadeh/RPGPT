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


class Goal:
    """
    Class to store a goal of a player.
    Handles the title, description, status, and completion status of the goal.
    """
    def __init__(self, title: str, goal: str, xp_reward: int, gold_reward: int, status: str = "Active"):
        """
        Initializes the Goal object with the provided title, description, and status.
        """
        self.title = title
        self.goal = goal
        self.xp_reward = xp_reward
        self.gold_reward = gold_reward
        self.status = status

    def complete(self):
        """
        Completes the goal.
        """
        self.status = "Completed"

    def fail(self):
        """
        Fails the goal.
        """
        self.status = "Failed"

    def to_dict(self) -> dict:
        """
        Converts the Goal object to a dictionary.

        :return: the dictionary representation of the Goal object
        """
        return {
            "title": self.title,
            "description": self.goal,
            "status": self.status,
            "xp_reward": self.xp_reward,
            "gold_reward": self.gold_reward
        }

    @staticmethod
    def from_dict(data: dict) -> 'Goal':
        """
        Converts a dictionary to a Goal object.

        :param data: the dictionary to convert
        :return: the Goal object created from the dictionary
        """
        if "status" not in data:
            data["status"] = "Active"
        if "gold_reward" not in data:
            data["gold_reward"] = 0
        if "goal" not in data:
            data["goal"] = data["description"]
        return Goal(data["title"], data["goal"], data["xp_reward"], data["gold_reward"], data["status"])

    def __str__(self):
        return str(self.to_dict())

    def __repr__(self):
        return self.__str__()

    def __dict__(self):
        return self.to_dict()

    def toJSON(self):
        return json.dumps(self.to_dict(), indent=4)

    def __hash__(self):
        return hash(self.to_dict())

    def __eq__(self, other):
        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        return self.to_dict() != other.to_dict()

    def is_active(self):
        return self.status == "Active"


class Quest:
    """
    Class to store a quest of a player.
    Handles the title, description, status, and completion status of the quest.
    """
    def __init__(self, title: str, quest: str, xp_reward: int, gold_reward: int, goals: dict[str, Goal], status: str = "Active"):
        """
        Initializes the Quest object with the provided title, description, and status.
        """
        self.title = title
        self.quest = quest
        self.xp_reward = xp_reward
        self.gold_reward = gold_reward
        self.status = status
        self.goals = goals

    def complete(self):
        """
        Completes the quest.
        """
        self.status = "Completed"

    def fail(self):
        """
        Fails the quest.
        """
        self.status = "Failed"

    def to_dict(self) -> dict:
        """
        Converts the Quest object to a dictionary.

        :return: the dictionary representation of the Quest object
        """
        return {
            "quest_title": self.title,
            "quest_description": self.quest,
            "status": self.status,
            "quest_xp_reward": self.xp_reward,
            "quest_gold_reward": self.gold_reward,
            "goals": {goal: self.goals[goal].to_dict() for goal in self.goals.keys()}
        }

    @staticmethod
    def from_dict(data: dict) -> 'Quest':
        """
        Converts a dictionary to a Quest object.

        :param data: the dictionary to convert
        :return: the Quest object created from the dictionary
        """
        if isinstance(data["goals"], list):
            goals = {goal["title"]: Goal.from_dict(goal) for goal in data["goals"]}
        else:
            goals = {goal: Goal.from_dict(data["goals"][goal]) for goal in data["goals"].keys()}
        if "status" not in data:
            data["status"] = "Active"
        if "quest_gold_reward" not in data:
            data["quest_gold_reward"] = 0
        return Quest(data["quest_title"], data["quest_description"], data["quest_xp_reward"], data["quest_gold_reward"], goals, data["status"])

    def generate_dict_for_action(self) -> dict:
        """
        Generates a dictionary for the action based on the quest.

        :return: the dictionary for the action
        """
        return {
            "quest_title": self.title,
            "quest_description": self.quest,
            "goals": self.get_active_goals_list()
        }

    def __str__(self):
        return str(self.to_dict())

    def __repr__(self):
        return self.__str__()

    def __dict__(self):
        return self.to_dict()

    def toJSON(self):
        return json.dumps(self.to_dict(), indent=4)

    def __hash__(self):
        return hash(self.to_dict())

    def __eq__(self, other):
        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        return self.to_dict() != other.to_dict()

    def is_active(self):
        return self.status == "Active"

    def get_active_goals_list(self):
        """
        Returns a list of active goals.

        :return: a list of active goals
        """
        temp_goals = [goal.to_dict() for goal in self.goals.values() if goal.is_active()]
        for goal in temp_goals:
            del goal["status"]
            del goal["xp_reward"]
            del goal["gold_reward"]
        return temp_goals


class SaveData:
    """
    Class to store the save data of a player.
    Handles the story, shop, goals, theme, background, level, experience points, action points, skills,
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
            generated_inventory = generated_theme.generate_empty_inventory(background)
            if inventory is not None:
                if isinstance(inventory, dict):
                    generated_inventory.merge_with(Inventory(inventory))
                elif isinstance(inventory, Inventory):
                    generated_inventory.merge_with(inventory)
                else:
                    raise ValueError("Inventory must be a dictionary or an Inventory object.")

            # initialize the SaveData object with the generated data
            self.story = {}
            self.shop = Shop()
            self.quest = None
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
        self.quest = Quest.from_dict(data["quest"]) if data["quest"] else None
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
            "quest": self.quest.to_dict() if self.quest else None,
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

    def init_story(self):
        """
        Initializes the story of the player.
        Includes setting the history, scene, prompt, image, status, goal, health, options, rates, advantages, levels,
        and experience points.
        """
        skills = list(self.skills.keys())
        self.story = {
            "history": [],
            "scene": "",
            "prompt": "",
            "img": "",
            "status": "",
            "health": 5,
            "options": ["Wake up", "Look around", "Stand up"],
            "rates": [1, 1, 1],
            "advantages": [skills[0], skills[1], skills[2]],
            "levels": [0, 0, 0],
            "experience": [0, 0, 0]
        }
        self.shop.close()

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
        if "options" in result and result["health"] > 0:
            self.story["options"] = [remove_init_num(option) for option in result["options"] if option != ""]
            self.story["rates"] = result["rates"]
            self.story["advantages"] = [skill if skill in list(self.skills.keys()) else list(self.skills.keys())[0] for skill in result["advantages"]]
            self.story["levels"] = result["level"]
            self.story["experience"] = result["experience"]
        else:
            self.story["options"] = []
        if "new_location" in result:
            self.background["location"] = result["new_location"]
        self.add_xp(result_xp)
        self.story["status"] = result["action_result"]
        self.shop.close()
        self.update_quest(result["quest"])

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

    def set_quest(self, quest: dict):
        """
        Sets the quest of the player based on the provided quest.
        The quest must be in the following format:
        {
            "title": "Quest Title",
            "quest": "Quest Description",
            "xp_reward": 100,
            "gold_reward": 50,
            "goals": {
                "goal1": {
                    "title": "Goal Title",
                    "goal": "Goal Description",
                    "xp_reward": 50,
                    "gold_reward": 25
                },
                "goal2": {
                    "title": "Goal Title",
                    "goal": "Goal Description",
                    "xp_reward": 50,
                    "gold_reward": 25
                }
            }
        }

        :param quest: the quest to be set
        """
        self.quest = Quest.from_dict(quest)

    def update_quest(self, updater_output: dict):
        """
        Updates the player's goals based on the updater's output.
        The updater result must be in the following format:
        {
            "completed": [goalTitle1, goalTitle2, ...],
            "failed": [goalTitle1, goalTitle2, ...],
            "new": [goal3, goal4, ...]
        }

        :param updater_output: The result of the updater.
        """
        if "quest_completed" in updater_output:
            if updater_output["quest_completed"] == 'completed':
                self.quest.complete()
                self.add_xp(self.quest.xp_reward)
                self.coins += self.quest.gold_reward
                self.background["backstory"] = updater_output["new_backstory"]
            else:
                self.quest.fail()
            return

        for goal in updater_output["completed"]:
            if goal not in self.quest.goals:
                continue
            self.quest.goals[goal].complete()
            self.add_xp(self.quest.goals[goal].xp_reward)
            self.coins += self.quest.goals[goal].gold_reward
        for goal in updater_output["failed"]:
            if goal not in self.quest.goals:
                continue
            self.quest.goals[goal].fail()
        for goal in updater_output["new"]:
            if goal["title"] in self.quest.goals:
                continue
            if "gold_reward" not in goal:
                goal["gold_reward"] = 0
            self.quest.goals[goal["title"]] = Goal(goal["title"], goal["goal"], goal["xp_reward"], goal["gold_reward"])
