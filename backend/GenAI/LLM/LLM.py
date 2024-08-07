import logging

from backend.GenAI.LLM.models.ChatGPT import ChatGPT
from backend.Types.SaveData import SaveData
from backend.Types.Theme import Theme
from backend.GenAI.LLM.models.ModelClass import Model


def image_prompt(subject: str):
    return f"the best prompt for an image generator to generate a pencil sketch of {subject} in the following formula: \
    A pencil sketch of [adjectives] [subject] in a [environment], detailed, realistic, trending on \
    artstation, in style of [famous artist 1], [famous artist 2], [famous artist 3]."


class LLM:
    model: Model = ChatGPT()

    def write_history(self, history: list[str]) -> str:
        """
        Turns the history list into a string, trimming it if it's too long.

        :param history: the history to be trimmed
        :return: the trimmed history as a string
        """
        history_limit = 2 * self.model.history_window_size
        written_history = ""
        history_to_write = history

        if len(history) > history_limit:
            history_to_write = history[len(history) - history_limit:]

        for idx, part in enumerate(history_to_write):
            if idx % 2 == 0:
                written_history += "(player action: " + part + ") "
            else:
                written_history += part + " "

        return written_history

    # ---------------------------------------------- #
    # ----------------- Generators ----------------- #
    # ---------------------------------------------- #

    def test(self) -> str:
        return self.model.generate("test", "test")

    def generate_backstory(self, theme: Theme, background: dict) -> dict:
        backstory_generator_input = {
            "inventory": theme.generate_empty_inventory(background),
            "background": background
        }
        logging.debug(f"Backstory generator input: {backstory_generator_input}")
        return self.model.generate_json(self.backstory_system(theme, background), str(backstory_generator_input))

    def generate_action_result(self, data: SaveData, action: str, action_result: str) -> dict:
        action_json = {
            "history": self.write_history(data.story["history"]),
            "choice": action,
            "result": action_result,
            "current_quest": data.quest.generate_dict_for_action(),
            "health": data.story["health"],
            "inventory": data.inventory,
            "coins": data.coins
        }
        logging.debug(f"Action JSON: {action_json}")

        result = self.model.generate_json(self.storyteller_system(data), str(action_json))
        if result["status"] == "success" and "options" in result["result"] and len(result["result"]["options"]) > 0 and not isinstance(result["result"]["options"][0], str):
            logging.debug(f"BAD RESULT! Action result: {result['result']}")
            logging.debug(f"Trying again...")
            result = self.model.generate_json(self.storyteller_system(data), str(action_json))
            if result["status"] == "success" and not isinstance(result["result"]["options"][0], str):
                logging.debug(f"BAD RESULT AGAIN! Action result: {result['result']}")
                logging.debug(f"Failed to generate a valid result!")
                return {"status": "error", "reason": "Failed to generate a valid result!"}
        return result

    def generate_custom_action(self, data: SaveData, new_action: str) -> dict:
        action_json = {
            "desired_action": new_action,
            "history": self.write_history(data.story["history"]),
            "current_inventory": data.inventory,
            "current_coins": data.coins,
            "current_scene": data.story["scene"],
        }
        logging.debug(f"Action JSON: {action_json}")
        return self.model.generate_json(self.action_system(data), str(action_json))

    def generate_quest(self, data: SaveData) -> dict:
        quest_generator_input = {
            "background": data.background,
            "history": self.write_history(data.story["history"]),
            "current_scene": data.story["scene"],
            "inventory": data.inventory
        }
        logging.debug(f"Quest generator input: {quest_generator_input}")
        return self.model.generate_json(self.quest_system(data.theme), str(quest_generator_input))

    def update_quest(self, data: SaveData, action: str, new_scene: str, inventory: dict) -> dict:
        if data.quest is None:
            return {"status": "error", "reason": "No active quest!"}
        quest_updater_input = {
            "background": data.background,
            "history": self.write_history(data.story["history"] + ["(player action: " + action + ") "]),
            "current_scene": new_scene,
            "inventory": inventory,
            "quest": data.quest.generate_dict_for_action()
        }
        logging.debug(f"Quest updater input: {quest_updater_input}")
        return self.model.generate_json(self.quest_update_system(data.theme), str(quest_updater_input))

    def generate_shop(self, data: SaveData) -> dict:
        shop_generator_input = {
            "inventory": data.inventory,
            "background": data.background
        }
        logging.debug(f"Shop generator input: {shop_generator_input}")
        return self.model.generate_json(self.shop_system(data.theme, data.inventory.categories),
                                        str(shop_generator_input))

    # ---------------------------------------------- #
    # ------------ Prompt Constructors ------------- #
    # ---------------------------------------------- #

    def backstory_system(self, theme: Theme, background: dict):
        extra_fields = theme.get_generated_extra_fields(background)
        extra_fields_str = ""
        for field in extra_fields:
            extra_fields_str += f"{field['extra_field']}: {field['extra_field_value']}, "

        return f"You are the Game Master, narrating a text-based {theme} adventure game. \
        Your current role is to generate the player's backstory. \
        \
        I will provide you in json format the player's background and details. \
        \
        You will reply with a single json format containing the following fields:\
        name: the player's character name. \
        {extra_fields_str} \
        backstory: The player's character backstory. Don't copy the details field from the input, write it yourself. \
        traits: an array of 3 traits the player has, like 'Smart', 'Sarcastic', 'Honest', 'Kind', 'Arrogant', etc. \
        starting_location: the name of the player's starting location, fitting the {theme} theme. \
        inventory: a dictionary of items the player initially equips based on his backstory, in the json format i gave \
        them in. Each item must be a single string. \
        character_prompt: {image_prompt('''this character''')} You must include in the prompt the fact that the character's \
        gender is {background['gender']}. \
        scene_prompt: {image_prompt('''the starting location''')} \
        \
        The backstory should be one or two short sentences describing the player's background. \
        It should be creative, unique, hinting a rich world setting, \
        and should be consistent with the player's background and the {theme} theme. \
        Keep the inventory minimal, no more than 2 items. \
        \
        " + self.model.sys_footer()

    def storyteller_system(self, data: SaveData):
        theme = data.theme
        background = data.background
        skills = list(data.skills.keys())

        return (f"You are the Game Master, narrating a text-based {theme} adventure game. \
        Guide the player through an exciting {theme} world filled with secrets to uncover, puzzles to solve, exciting \
        twists and challenges to beat, fitting the {theme} theme. \
        Adapt the story to the player's choices and ensure they experience a thrilling and engaging adventure. \
        Make sure to keep the story's history so far in mind and provide a consistent and immersive experience. \
        If the player has a quest and goals, make sure to include them in the story. \
        If not, aim the story towards a new quest. \
        \
        Player's background: {background} \
        \
        I will provide you in json format the following: \
        A history of the story so far, \
        the player's choice of action, \
        weather the action was successful or not, \
        the player's current quest and goals, \
        the player's current health (out of 5), \
        the player's current inventory (items), \
        and the player's current amount of coins. \
        \
        You will reply with a single json format containing the following fields: \
        scene: a short description of what the player sees only in the new scene unfolding according to the success of \
        the player's action and the starting location indicated in the background. \
        The scene has to be creative, imagination igniting, and consistent the world.\
        If the player's health reaches 0, describe the player's death. \
        Do not include the player's next choice in the scene. \
        new_location: the name of the player's new current location, fitting the {theme} theme. \
        Include the new_location field only when the player's action leads to a different location. \
        options: an array of 3 possible actions the player can take. If it involves using or receiving coins, state \
        the amount of coins, but do not spend it unless chosen! \
        IMPORTANT - Do not present options involving using items the player doesn't currently have in his inventory! \
        rates: an array of 3 rates for the options, from 0 to 1, representing the probability of the success of each \
        option. \
        advantages: an array of 3 advantages for the options, indication what skill will improve the success of each \
        option (possible skills: {skills}). \
        level: an array of 3 levels for the options, each in range [2, 30], representing the required level of the \
        player in the skill for the bonus. \
        experience: an array of 3 experience points values for the options, each in range [0, 15], representing the \
        experience points the player will gain if he chooses this option. \
        health: the updated player's health (if he took a physical hit from any source, reduce the original by 1).\
        inventory: an dictionary of items the player equips, updated according to the new scene and in the json format \
        I gave them in. \
        IMPORTANT - Do not add items to the player's inventory unless he chose an option resulting in receiving an \
        item, or the player receives an item in the scene you provide! \
        coins: the updated player's amount of coins. \
        prompt: {image_prompt('''this scene''')} \
        Keep the prompt in the {theme} theme and coherent with the story so far, and don't include the player in it! \
        \
        IMPORTANT: When the player's health reaches 0, do not include the options field! \
        \
        ") + self.model.sys_footer()

    def action_system(self, data: SaveData):
        theme = data.theme
        history = data.story["history"]
        skills = list(data.skills.keys())

        return f"You are the Game Master, narrating a text-based {theme} adventure game. \
        Your current role is to check weather the player's desired action is valid and generate it's properties. \
        A valid action is an action that the player can take according to his current inventory, coins, \
        the world's logic, and the story history so far. \
        \
        I will provide you in json format the following: \
            The player's desired action, \
            The current history, \
            The player's current inventory (items), \
            The player's current amount of coins. \
        \
        You will reply with a single json format containing the following fields: \
            valid: a string value indicating weather the player's action is valid or not: 'yes' or 'no'. \
            If the action is valid, provide the following fields: \
            rate: a float value in range [0, 1] representing the probability of the success of the action. \
            advantage: a string representing what skill will improve the success of the action. \
            (possible skills: {skills}). \
            level: an integer value in range [2, 30] representing the required level of the player in the skill for \
            the bonus. \
            experience: an integer value in range [0, 15] representing the experience points the player will gain if \
            he chooses this action. \
        \
        Follows is the player's story history so far: {history} \
        \
        " + self.model.sys_footer()

    def quest_system(self, theme: Theme):
        return (f"You are the Game Master, narrating a text-based {theme} adventure game. \
        Your current role is to generate a main quest for the player to achieve, with 3 sub-goals. \
        The main quest should be long, challenging, and engaging, fitting the {theme} theme, and consistent with the \
        player's backstory, inventory and the history so far (if any). \
        \
        I will provide you in json format the following: \
            The player's background, \
            The player's history, \
            The player's current scene, \
            The player's current inventory (items). \
        \
        You will reply with a single json format containing the following fields: \
        quest_title: the main quest's title. \
        quest_description: a short description of the main quest, being clear and direct, so it's easy to tell if the \
        player achieved it or not, and consistent with the player's backstory, inventory and the {theme} theme. \
        quest_xp_reward: the amount of experience points the player will receive if he achieves the main quest, in \
        range [0, 1000]. \
        quest_gold_reward: add this field only if the main quest completion means the player receives coins from the \
        quest requester, and set it to the amount of coins the player will receive, in range [0, 5000]. \
        goals: a list of 3 sub-goals in dict format, each containing the following fields: \
            - title: the sub-goal's title. \
            - goal: a short description of what the player needs to achieve, being clear and direct, so it's easy to \
            tell if the player achieved them or not, and consistent with the player's backstory, inventory and the \
            {theme} theme. \
            - xp_reward: the amount of experience points the player will receive if he achieves the sub-goal, in range \
            [0, 100]. \
            - gold_reward: add this field only if the sub-goal completion means the player receives coins from the \
            goal requester, and set it to the amount of coins the player will receive, in range [0, 250]. \
        \
        The main quest should build upon the world story and player's background. \
        The sub-goals should be long-term goals, which the player will need to work on for a while, each building upon \
        the previous one, and leading to the main quest. \
        If the quest's or goals' text contains a ' character, escape it with a backslash. \
        \
        ") + self.model.sys_footer()

    def quest_update_system(self, theme: Theme):
        return (f"You are the Game Master, narrating a text-based {theme} adventure game. \
        Your current role is to check weather the player's quest or goals are achieved and update the player's goals \
        and quest. \
        If you have a new goal to add to the player, add it according to the current scene, in the context of the \
        player's backstory, history, inventory and other goals. \
        Only add new goals if the current scene generates a new goal for the player to achieve in order to progress in \
        the main quest. \
        \
        I will provide you in json format the following: \
            The player's background, \
            The player's history, \
            The player's current scene, \
            The player's current inventory (items), \
            The player's current quest and goals. \
        \
        If the quest has completed or failed, reply with a single json format containing the following fields: \
            quest_completed: a string value indicating weather the player's quest is completed or failed: 'completed' \
            or 'failed'. \
            new_backstory: an updated player's backstory according to the result of the quest (keep it short!). \
        Else, you will reply with a single json format containing the following fields: \
            completed: a list of the player's completed goals' titles. \
            failed: a list of the player's failed goals' titles. \
            new: a list of the player's new goals in dict format, each containing the following fields: \
            - title: the goal's title. \
            - goal: a short description of what the player needs to achieve, being clear and direct, so it's easy to tell if \
            the player achieved them or not, and consistent with the player's backstory, inventory and the {theme} theme. \
            - xp_reward: the amount of experience points the player will receive if he achieves the goal, in range [0, 100].\
            - gold_reward: add this field only if the goal completion means the player receives coins from the goal \
            requester, and set it to the amount of coins the player will receive, in range [0, 250]. \
        \
        Keep the new goals long-term goals, which the player will need to work on for a while. \
        IMPORTANT: DO NOT add goals unless you have a good reason to do so! Not every scene presents a new goal! \
        And no need to add several goals at once! \
        the new goals should be decided according to the current scene, in the context of the player's backstory, \
        history, inventory, other goals and most importantly, the main quest. \
        If the goal's text contains a ' character, escape it with a backslash. \
        \
        ") + self.model.sys_footer()

    def shop_system(self, theme: Theme, inv_categories: list[str]):
        return (f"You are the Game Master, narrating a text-based {theme} adventure game. \
        Your current role is to run a shop for the player to interact with. \
        \
        I will provide you in json format details about the player's character, \
        including his backstory and current inventory (items). \
        \
        If the player's location doesn't allow for a shop to be available, such as a secluded area or a place where it \
        makes no sense to have a shop, reply with a single json format containing the key 'problem' with the value \
        'No Shop'. \
        Else, you will reply with a single json format containing the following fields: \
        sold_items: a list of items the player can buy, in the json format i gave them in, only difference is that \
        each item is in the format item_name: (category, price). \
        buy_items: a list of items the player has in his inventory that the shopkeeper can buy, in the json format I \
        gave them in, only difference is that each item is in the format item_name: (category, price). \
        Item categories must be from: {inv_categories}. \
        Item prices must be in range [1, 5000]. \
        shopkeeper_description: a short description of who the shopkeeper is, like 'a tavern keeper', 'a blacksmith', 'an old woman', etc. \
        shopkeeper_recommendation: shopkeeper's recommendation for the player, in the shopkeeper's words. \
        prompt: {image_prompt('''the shop's merchandise''')} \
        Keep the prompt in the {theme} theme, focus on the items and dont include the player in the prompt. \
        \
        The sold items should be consistent with the player's backstory, inventory and the {theme} theme. \
        Item categories must be from: {inv_categories}. \
        The shopkeeper's recommendation should consist of either pushing a sold item, or trying to buy an item from \
        the player. \
        Note, That the shopkeeper knows the player's character well, and is a snarky person. \
        \
        ") + self.model.sys_footer()
