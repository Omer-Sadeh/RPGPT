import time
import backend.GenAI.T2I as T2I
from backend.Types.Theme import Theme
from backend.GenAI.LLM.LLM import LLM
from backend.Utility import *
from backend.Types.Inventory import Inventory
from backend.Game.GameUtils import *
from backend.Types.Themes import get_theme, Available_Themes
from backend.Database.Database import DataBase
from backend import SNS


class Game:
    DB = DataBase()
    LLM = LLM()

    # ----------------------------------------------------- #
    # ---------------------- LLM Calls -------------------- #
    # ----------------------------------------------------- #

    @error_wrapper
    def generate_action_result(self, username: str, save_name: str, action: str) -> dict:
        """
        Generate the result of an action based on the player's data and the chosen action.
        Method calls the LLM model to generate the result.

        :param username: The username of the player.
        :param save_name: The name of the save.
        :param action: The chosen action.
        :return: The result of the action.
        """
        logging.info(f"Generating action result for {action}.")

        # Retrieve the story data and the index of the chosen action
        player_data = self.DB.get_save_data(username, save_name)
        action_index = player_data.story["options"].index(action)

        # Calculate the success rate of the action and generate the result string
        success_rate = calculate_success_rate(player_data, action_index)
        action_result = probability_function(success_rate)
        logging.debug(f"Success rate: {success_rate}, Action result: {action_result}")

        # Call the LLM model to generate the result of the action
        result = self.LLM.generate_action_result(player_data, action, action_result)
        if result["status"] == "error":
            logging.error(f"LLM model error: {result['reason']}")
            raise Exception(result["reason"])

        # Process the result and return it
        result = result["result"]
        result["action_result"] = action_result
        logging.info(f"Generated action result for {action}.")
        logging.debug(f"Action result: {result}")

        quest_result = self.LLM.update_quest(player_data, action, result["scene"], result["inventory"])
        if quest_result["status"] == "error":
            logging.error(f"LLM model error: {quest_result['reason']}")
            raise quest_result["reason"]
        result["quest"] = quest_result["result"]
        logging.debug(f"Quest update result: {result['quest']}")

        return result

    def generate_story_cache(self, username: str, save_name: str, img_flag: bool = False) -> None:
        """
        Generate the results of all the actions into the cache to speed up the story advancement.
        This method is called after each action to generate the results of the next actions, asynchronously.

        :param username: The username of the player.
        :param save_name: The name of the save.
        :param img_flag: Whether to generate an image for the prompt.
        """
        logging.info("Generating story cache...")

        try:
            # Load the player's data
            player_data = self.DB.get_save_data(username, save_name)

            # Initialize the shop data and save it
            if player_data.shop.status == "closed":
                logging.info("Initializing shop...")
                start_promise(self.get_shop, username, save_name, img_flag)

            # Initialize the cache with "in progress" for each action
            self.DB.delete_all_cache(username, save_name)
            for action in player_data.story["options"]:
                self.DB.cache(username, save_name, action, "in progress")
        except Exception as e:
            logging.exception(f"Error initializing story cache:")
            return

        # Generate the results of each action asynchronously
        choices_promises = [start_promise(self.generate_action_result, username, save_name, choice)
                            for choice in player_data.story["options"]]

        # Generate the results of each action and update the cache
        for idx, action in enumerate(player_data.story["options"]):
            try:
                res = await_promise(choices_promises[idx])
                if res["status"] == "error":
                    self.DB.delete_cache(username, save_name, action)
                    logging.error(f"Error generating cache for option {action}: {res['reason']}")
                else:
                    self.DB.cache(username, save_name, action, res["result"])
                    logging.debug(f"Generated cache for option {action}: {res['result']}")
            except Exception as e:
                self.DB.delete_cache(username, save_name, action)
                logging.exception(f"Error generating story cache:")

    @error_wrapper
    def generate_shop(self, username: str, save_name: str, data: SaveData, img_flag: bool = False) -> dict:
        """
        Generate the shop for the player based on the player's data.

        :param username: The username of the player.
        :param save_name: The name of the save.
        :param data: The player's data.
        :param img_flag: Whether to generate an image for the shop.
        :return: The generated shop.
        """
        logging.info("Generating shop...")

        # Call the LLM model to generate the shop and save it
        result = self.LLM.generate_shop(data)
        if result["status"] == "success":
            result = result["result"]
            logging.debug(f"Generated shop: {result}")

            result["image"] = None
            if img_flag and "prompt" in result:
                logging.info("Generating shop image..." if not DEBUG else "Generating shop image. Prompt: " + result["prompt"])
                img = T2I.generate(result["prompt"])
                if img["status"] == "error":
                    logging.error(f"Shop generation image error: {img['reason']}")
                    raise Exception(img["reason"])
                else:
                    self.DB.save_image(username, save_name, "shop", img["result"])
                logging.info("Generated shop image.")
            logging.info("Generated shop.")
            return result
        else:
            logging.error(f"Shop generation LLM model error: {result['reason']}")
            raise Exception(result["reason"])

    @error_wrapper
    def generate_backstory(self, theme: Theme, background: dict) -> dict:
        """
        Generate an initial backstory for the player based on the player's theme and background.
        This is done by calling the LLM model with the backstory generator.

        :param theme: The player's theme.
        :param background: The player's background.
        """
        # Call the LLM model to generate the backstory and return it
        result = self.LLM.generate_backstory(theme, background)
        if result["status"] == "success":
            result = result["result"]
            logging.info("Generated backstory: " + str(result))
            result["inventory"] = Inventory(result["inventory"]).to_dict()
            logging.info("Generated backstory.")
            logging.debug(f"Generated backstory: {result}")
            return result
        else:
            logging.error(f"Backstory generation LLM model error: {result['reason']}")
            raise Exception(result["reason"])

    # ----------------------------------------------------- #
    # ------------------------ Util ----------------------- #
    # ----------------------------------------------------- #

    def initialize_save(self, username: str, save_name: str, img_flag: bool = False) -> SaveData:
        """
        Initialize the story for the player when the save is loaded.
        Used for resetting the cache and status of the story when the save is loaded.
        """
        # Load the player's data
        player_data = self.DB.get_save_data(username, save_name)
        logging.debug(f"Story data: {player_data.story}")

        # Reset the story data and cache
        player_data.story["status"] = ""
        if player_data.shop.status == "generating":
            player_data.shop.close()
            logging.info("Resetting shop.")
            self.DB.save_game_data(username, save_name, player_data)

        start_promise(self.generate_story_cache, username, save_name, img_flag)

        return player_data

    # ----------------------------------------------------- #
    # ------------------------ API ------------------------ #
    # ----------------------------------------------------- #

    @APIEndpoint
    def system_startup(self) -> list[str]:
        """
        Get the status of the system.
        This is done by calling all the GenAI with a testing prompt.

        :return: The status of each model.
        """
        # Call the LLM and T2I GenAI with a testing prompt.
        # This is done in a non-blocking way to speed up the response.
        test_llm_promise = start_promise(self.LLM.test)
        test_t2i_promise = start_promise(T2I.generate, "system_test")
        test_llm = await_promise(test_llm_promise)
        test_t2i = await_promise(test_t2i_promise)

        # Process the results and return the status of each model
        result = []
        if test_llm["status"] == "error":
            logging.warning(f"LLM model error: {test_llm['reason']}")
            result.append("LLM")
        if test_t2i["status"] == "error":
            logging.warning(f"T2I model error: {test_t2i['reason']}")
            result.append("T2I")

        # Return the status of each model
        return result

    @APIEndpoint
    def get_saves_list(self, username: str) -> list:
        """
        Get the list of all the saves.

        :param username: The username of the player.
        :return: The list of all the saves and their respective images.
        """
        saves = self.DB.saves_list(username)
        return [{"id": save, "name": saves[save], "image": self.DB.get_save_image(username, save, 'character')} for save in saves.keys()]

    @APIEndpoint
    def get_available_themes(self) -> dict:
        """
        Get the list of all the available themes and their required fields.

        :return: The list of all the available themes.
        """
        return {theme.name: {"name": theme.name, "fields": theme.fields} for theme in Available_Themes}

    @APIEndpoint
    def load_save(self, username: str, save_name: str, img_flag: bool = False) -> dict:
        """
        Load a save's data.

        :param username: The username of the player.
        :param save_name: The name of the save.
        :param img_flag: Whether to generate an image for the character.
        :return: The data of the save.
        """
        return self.initialize_save(username, save_name, img_flag).to_dict()

    @APIEndpoint
    def new_save(self, username: str, theme_name: str, background: dict, img_flag: bool) -> str:
        """
        Create a new save with the given data.

        :param username: The username of the player.
        :param theme_name: The theme of the save.
        :param background: The background of the save.
        :param img_flag: Whether to generate an image for the character.
        """
        if len(self.DB.saves_list(username).keys()) >= 5:
            logging.error("Too many saves.")
            raise CustomException("Too many saves.")

        logging.info(f"Creating new save with theme: {theme_name} and background: {background}")

        # validation background input
        for field in background:
            decision = SNS.llm_input(background[field])
            if not decision:
                raise CustomException("Invalid background input: " + field + ": " + str(background[field]) + ", " + decision.reason)
        try:
            theme = get_theme(theme_name)
        except ValueError:
            raise CustomException("Invalid theme.")
        for field in theme.get_all_required_fields(background):
            if field not in background:
                raise CustomException("Missing required field: " + field)

        # Generate the backstory for the player
        result = self.generate_backstory(theme, background)
        if result["status"] == "error":
            raise Exception(result["reason"])
        result = result["result"]
        logging.debug(f"Backstory generation result: {result}")

        # Process the result and add the generated extra fields to the background
        background["name"] = result["name"]
        background["backstory"] = result["backstory"]
        background["traits"] = result["traits"]
        background["location"] = result["starting_location"]
        for extra_field in theme.get_generated_extra_fields(background):
            field_name = extra_field["extra_field"]
            background[field_name] = result[field_name]

        # remove the "details" field
        background.pop("details", None)

        # process and validate the save name
        save_name = str(random.randint(1000, 999999999999999))

        # Create the save with the given data
        save_data = SaveData(theme=theme_name, background=background, inventory=result["inventory"])
        save_data.init_story()

        # Generate and initial main quest
        quest_result = self.LLM.generate_quest(save_data)
        if quest_result["status"] == "error":
            raise Exception(quest_result["reason"])
        logging.debug(f"Quest generation result: {quest_result['result']}")
        save_data.set_quest(quest_result["result"])

        # Save the data and generate the story cache
        self.DB.create_save(username, save_name, save_data)
        start_promise(self.generate_story_cache, username, save_name, img_flag)

        # Generate the character images if needed
        if img_flag:
            char_img_promise = start_promise(T2I.generate, result["character_prompt"])
            scene_img_promise = start_promise(T2I.generate, result["scene_prompt"])

            char_img = await_promise(char_img_promise)
            scene_img = await_promise(scene_img_promise)

            if char_img["status"] == "error":
                raise Exception("char image error: " + char_img["reason"])
            else:
                self.DB.save_image(username, save_name, "character", char_img["result"])

            if scene_img["status"] == "error":
                raise Exception("scene image error: " + scene_img["reason"])
            else:
                self.DB.save_image(username, save_name, "scene", scene_img["result"])

        return save_name

    @APIEndpoint
    def delete_save(self, username: str, save_name: str):
        """
        Delete a save.

        :param username: The username of the player.
        :param save_name: The name of the save.
        """
        self.DB.delete_save(username, process_save_name(save_name))
        self.DB.delete_all_cache(username, save_name)

    @APIEndpoint
    def advance_story(self, username: str, save_name: str, action: str, img_flag: bool) -> str:
        """
        Advance the story for the player by processing the result of the chosen action, and then updating the story data.
        This is done by generating the result of the action and updating the story data.

        Note: This method first checks if the result is already generated in the cache to speed up the process.
        After the result is generated, the method calls the cache generator to generate the results of the next actions,
        asynchronously.

        :param username: The username of the player.
        :param save_name: The name of the save.
        :param action: The chosen action.
        :param img_flag: Whether to generate an image for the prompt.
        :return: The status of the story after advancing.
        """
        player_data = self.DB.get_save_data(username, save_name)

        if player_data.story["health"] <= 0:
            logging.error("Player is dead.")
            raise CustomException("Player is dead.")

        if action not in player_data.story["options"]:
            logging.error(f"Invalid action: {action}")
            raise CustomException("Invalid action.")

        try:
            # Initialize the story status and load the player's data
            player_data.story["status"] = "advancing"
            logging.debug(f"Action: {action}, Story data: {player_data.story}")
            self.DB.save_game_data(username, save_name, player_data)

            # Check if the result is already generated in the cache, and wait for it if it's in progress
            while True:
                cache_data = self.DB.get_cache(username, save_name, action)
                if cache_data and cache_data == "in progress":
                    time.sleep(1)
                else:
                    break
            logging.debug(f"Retrieved cache: {cache_data}")

            # Generate the result of the action
            if cache_data and cache_data != "in progress":  # If the result is already generated in the cache
                result = cache_data
                logging.debug(f"Retrieved result from cache: {result}")
            else:  # If the result is not generated in the cache (caused by an error while generating the cache)
                result = self.generate_action_result(username, save_name, action)
                if result["status"] == "error":
                    raise Exception(result["reason"])
                result = result["result"]
            logging.debug(f"Result: {result}")

            # Generate an image for the prompt if needed
            if img_flag:
                img = T2I.generate(result["prompt"])
                if img["status"] == "error":
                    logging.error(img["reason"] + "\n" + "prompt: " + result["prompt"])
                else:
                    self.DB.save_image(username, save_name, "scene", img["result"])

            # Update the story
            player_data.update_story(result, action)
            player_data.shop.close()
            player_data.advance_version()

            # Quest completion handling
            logging.debug(f"Quest status: {player_data.quest.status}")
            if player_data.quest.status == "Completed" or player_data.quest.status == "Failed":
                logging.info("Quest completed or failed. starting new quest.")
                quest_result = self.LLM.generate_quest(player_data)
                if quest_result["status"] == "error":
                    raise Exception(quest_result["reason"])
                player_data.set_quest(quest_result["result"])

            # Save the data and generate the story cache
            self.DB.save_game_data(username, save_name, player_data)
            if player_data.story["health"] > 0:
                start_promise(self.generate_story_cache, username, save_name, img_flag)

            return result["action_result"]
        except Exception as e:
            logging.exception(f"Error advancing story:")
            player_data.story["status"] = "error: " + str(e)
            self.DB.save_game_data(username, save_name, player_data)

    @APIEndpoint
    def create_new_option(self, username: str, save_name: str, new_action: str) -> str:
        """
        Create a new option for the player based on the player's data.

        :param username: The username of the player.
        :param save_name: The name of the save.
        :param new_action: The new action to add.
        :return: An error message if the action is invalid, otherwise an empty string.
        """
        # Load the player's data and update the story data
        player_data = self.DB.get_save_data(username, save_name)

        # check action guardrails
        if len(player_data.story["options"]) >= 5:
            logging.error("Too many actions.")
            raise CustomException("Too many existing options, can't add a new one.")
        if new_action in player_data.story["options"]:
            logging.error(f"Invalid action: {new_action}, already exists.")
            raise CustomException("Action already exists.")
        decision = SNS.llm_input(new_action)
        if not decision:
            logging.error(f"Invalid action: {new_action}, {decision.reason}")
            raise CustomException("Invalid action: " + decision.reason)

        # Call the LLM model to generate the result of the action
        result = self.LLM.generate_custom_action(player_data, new_action)
        if result["status"] == "error":
            raise Exception(result["reason"])

        # Process the result and return it
        result = result["result"]
        if result["valid"] == "no":
            logging.error(f"Invalid action: {new_action}")
            logging.debug(f"Custom action result: {result}")
            return "Invalid action. Please try a possible action."
        logging.info(f"Created new action: {new_action}")

        # Add the new action to the story data and save it
        player_data.story["options"].append(new_action)
        player_data.story["rates"].append(result["rate"])
        player_data.story["advantages"].append(result["advantage"] if result["advantage"] in player_data.skills.keys()
                                               else list(player_data.skills.keys())[0])
        player_data.story["levels"].append(result["level"] if isinstance(result["level"], int) else 0)
        player_data.story["experience"].append(result["experience"] if isinstance(result["experience"], int) else 0)
        self.DB.save_game_data(username, save_name, player_data)
        return "Created!"

    @APIEndpoint
    def spend_action_point(self, username: str, save_name: str, skill: str) -> None:
        """
        Spend an action point to increase a skill for the player.

        :param username: The username of the player.
        :param save_name: The name of the save.
        :param skill: The skill to increase.
        """
        # Load the player's data and check if the player has enough action points and the skill exists
        player_data = self.DB.get_save_data(username, save_name)

        if player_data.action_points <= 0:
            logging.error("No action points left.")
            raise CustomException("No action points left.")
        if skill not in player_data.skills.keys():
            logging.error("Skill not found.")
            raise CustomException("Skill not found.")

        # Update the player's data and save it
        player_data.action_points -= 1
        player_data.skills[skill] += 1
        player_data.advance_version()
        logging.info(f"Spent action point on skill: {skill}")
        self.DB.save_game_data(username, save_name, player_data)

    @APIEndpoint
    def get_shop(self, username: str, save_name: str, img_flag: bool) -> dict:
        """
        Produce the shop for the player based on the player's data.
        First, check if the shop is already generated, and if not, generate it.

        :param username: The username of the player.
        :param save_name: The name of the save.
        :param img_flag: Whether to generate an image for the shop.
        :return: The generated shop.
        """
        # Load the player's data
        player_data = self.DB.get_save_data(username, save_name)

        # Check if the shop is already generated
        while player_data.shop.status == "generating":
            player_data = self.DB.get_save_data(username, save_name)
            continue

        # Generate the shop if it is not already generated
        if player_data.shop.status == "closed":
            logging.info("No shop in cache.")
            player_data.shop.generating()
            self.DB.save_game_data(username, save_name, player_data)

            result = self.generate_shop(username, save_name, player_data, img_flag)
            if result["status"] == "error":
                logging.error(f"Shop generation error: {result['reason']}")
                player_data.shop.close()
                self.DB.save_game_data(username, save_name, player_data)
                raise Exception(result["reason"])
            result = result["result"]
            player_data.shop.stock(result)
            logging.info("Generated shop.")
            logging.debug(f"Generated shop: {result}")
            self.DB.save_game_data(username, save_name, player_data)
        elif player_data.shop.status == "unavailable":
            logging.error("Shop unavailable.")
            raise CustomException("Shop unavailable at player's location.")
        else:
            result = player_data.shop.to_dict()

        return result

    @APIEndpoint
    def buy_item(self, username: str, save_name: str, item_name: str) -> None:
        """
        Buy an item from the shop for the player.

        :param username: The username of the player.
        :param save_name: The name of the save.
        :param item_name: The item to buy.
        """
        # Load the player's data and check if the player has enough coins and doesn't own the item
        player_data = self.DB.get_save_data(username, save_name)

        category, price = player_data.shop.get_sold_item(item_name)
        logging.debug(f"Item: {item_name}, Category: {category}, Price: {price}")

        if player_data.coins < price:
            raise CustomException("Not enough coins.")
        if player_data.inventory.contains(item_name, category):
            raise CustomException("Item already owned.")

        # Update the player's data and save it
        player_data.inventory.add_item(item_name, category)
        player_data.coins -= price
        player_data.shop.item_sold(item_name)
        logging.info(f"Bought item: {item_name}")
        self.DB.save_game_data(username, save_name, player_data)

    @APIEndpoint
    def sell_item(self, username: str, save_name: str, item_name: str) -> None:
        """
        Sell an item to the shop for the player.

        :param username: The username of the player.
        :param save_name: The name of the save.
        :param item_name: The item to sell.
        """
        # Load the player's data and check if the player owns the item
        player_data = self.DB.get_save_data(username, save_name)

        if item_name not in player_data.shop.buy_items.keys():
            raise CustomException("I don't want this item.")

        category, price = player_data.shop.get_buy_item(item_name)
        logging.debug(f"Item: {item_name}, Category: {category}, Price: {price}")

        if not player_data.inventory.contains(item_name, category):
            raise CustomException("Item not owned.")

        # Update the player's data and save it
        player_data.inventory.remove_item(item_name, category)
        player_data.coins += price
        player_data.shop.item_bought(item_name)
        logging.info(f"Sold item: {item_name}")
        self.DB.save_game_data(username, save_name, player_data)

    @APIEndpoint
    def get_image(self, username: str, save_name: str, category: str) -> str:
        """
        Get the image of the last generated prompt, as a base64 string.

        :param username: The username of the player.
        :param save_name: The name of the save.
        :param category: The category of the image.
        """
        return self.DB.get_save_image(username, save_name, category)
