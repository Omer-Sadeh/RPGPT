import base64
import os
import io
import requests
from PIL import Image
from colorama import init, Fore, Back, Style
from simple_term_menu import TerminalMenu
from getpass import getpass

init(autoreset=True)
TOKEN = {
    "access_token": "",
    "gen_img": False
}


# ------------------------------------------- #
# ---------------- Utilities ---------------- #
# ------------------------------------------- #


def logout():
    TOKEN["access_token"] = ""
    env_file = open(".env", "r")
    lines = env_file.readlines()[:-1]
    env_file.close()
    env_file = open(".env", "w")
    env_file.write("\n".join([line.strip() for line in lines]))
    env_file.close()


def req(path, data=None, body=None) -> dict[str, any]:
    url = 'http://127.0.0.1:8000{}/'.format(path)
    try:
        # Build the headers
        headers = {"Authorization": "Bearer " + TOKEN["access_token"], "images": str(TOKEN["gen_img"])}

        # Send the request
        if data or body:
            params = {}
            if not body:
                body = {}
            if data:
                for key, value in data.items():
                    if isinstance(value, dict) or isinstance(value, list):
                        body[key] = value
                    else:
                        params[key] = value
            response = requests.post(url, params=params, json=body, headers=headers)
        else:
            response = requests.get(url, headers=headers)

        # Process the response
        if response.status_code != 200:
            if 400 <= response.status_code < 500:
                logout()
                if response.status_code == 401:
                    return {"status": "error", "reason": "Unauthorized. Please log in again."}
                if "message" in response.json():
                    return {"status": "error", "reason": response.json()["message"]}
                else:
                    return {"status": "error", "reason": "Failed communicating with server. " + response.reason}
            return {"status": "error",
                    "reason": "Failed communicating with server. " + response.reason + " (" + str(response.status_code) + ")"}
        return {"status": "success",
                "result": response.json()}

    except requests.exceptions.ConnectionError:
        return {"status": "error", "reason": "Failed communicating with server. Connection refused."}


def clear_line(n=1):
    LINE_UP = '\033[1A'
    LINE_CLEAR = '\x1b[2K'
    for _ in range(n):
        print(LINE_UP, end=LINE_CLEAR)


def clear_screen():
    print("\033c", end="")


def choose_from_list(prompt, options, preview_func=None, preview_title=""):
    def shortcut(num):
        if num < 10:
            return str(num)
        num = num - 9
        if num < 1 or num > 26:
            return " "
        else:
            return chr(num + 96)

    menu_options = ["[" + shortcut(idx + 1) + "] " + str(option) for idx, option in enumerate(options)]

    terminal_menu = TerminalMenu(menu_options, title=prompt + "\n", skip_empty_entries=True,
                                 preview_command=preview_func, preview_title=preview_title,
                                 menu_highlight_style=("bold", "fg_cyan"), menu_cursor_style=("bold", "fg_cyan"),
                                 shortcut_key_highlight_style=("bold", "fg_cyan"))
    choice = terminal_menu.show()

    chosen = options[choice]
    print(Style.BRIGHT + "Option chosen: " + Fore.LIGHTWHITE_EX + str(chosen) + "\n")

    return choice


def input_prompt(prompt, check_func=lambda _: True, error="Invalid input!", secret=False):
    print(Style.BRIGHT + prompt + Style.NORMAL, end="")
    if secret:
        answer = getpass("")
    else:
        answer = input()
    if not check_func(answer):
        invalid_choice(error)
        return input_prompt(prompt, check_func, error, secret)
    return answer


def invalid_choice(error="Invalid choice!"):
    print()
    print(Fore.RED + error + " Please try again.")
    print()


def proccess_print(text):
    print(Style.DIM + text)


def show_image(save):
    result = req("/image", {"save_name": save})
    if result["status"] == "error":
        return
    image = Image.open(io.BytesIO(base64.b64decode(result["result"])))
    image.show()


def yes_no_input(prompt):
    answer = input_prompt(prompt + " (Y/N): ")
    if answer.lower() == "y" or answer.lower() == "yes" or answer == "":
        return True
    elif answer.lower() == "n" or answer.lower() == "no":
        return False
    else:
        invalid_choice()
        return yes_no_input(prompt)


def divider(space=True):
    console_size = os.get_terminal_size().columns

    print() if space else None
    print("-" * console_size)
    print() if space else None


def bold_divider():
    line = "-" * os.get_terminal_size().columns
    print(Style.BRIGHT + Fore.LIGHTWHITE_EX + line)


def print_error(error):
    divider()
    print(Style.BRIGHT + Back.RED + "Error: " + error)
    print("Please try again.")
    divider()


# ------------------------------------------- #
# ------------- Game Components ------------- #
# ------------------------------------------- #


def print_inventory(inventory: dict):
    print("----- " + Style.BRIGHT + "Inventory" + Style.NORMAL + " -----")
    for category in inventory.keys():
        print(Style.BRIGHT + category + " |" + Style.NORMAL, end="")
        for item in inventory[category]:
            print(" ( " + str(item) + " )", end="")
        print()
    print("---------------------")


def print_background(background):
    divider(False)
    if "traits" in background:
        print(Style.BRIGHT + background["name"] + Style.NORMAL + " (" + ", ".join(background["traits"]) + ")", end="")
    else:
        print(Style.BRIGHT + background["name"], end="")
    print(" | ", end="")
    for field in background.keys():
        if field not in ["name", "backstory", "traits"]:
            print(Style.BRIGHT + field + ": " + Style.NORMAL + background[field], end="")
            print(" | ", end="")
    print()
    print(Style.BRIGHT + "Backstory: " + Style.NORMAL + background["backstory"])
    divider(False)


def generate_title():
    divider()
    print(Style.BRIGHT + Fore.GREEN + """
            .______      .______     _______ .______   .___________.
            |   _  \     |   _  \   /  _____||   _  \  |           |
            |  |_)  |    |  |_)  | |  |  __  |  |_)  | `---|  |----`
            |      /     |   ___/  |  | |_ | |   ___/      |  |     
            |  |\  \----.|  |      |  |__| | |  |          |  |     
            | _| `._____|| _|       \______| | _|          |__|     
          """)
    divider()


def show_story_status(data, action_res_message):
    print_background(data["background"])
    story = data["story"]
    print(Style.BRIGHT + Fore.RED + "Health: " + str(story["health"]), end="")
    print(" | ", end="")
    print(Style.BRIGHT + Fore.YELLOW + "Coins: " + str(data["coins"]), end="")
    print(" | ", end="")
    print(Style.BRIGHT + Fore.LIGHTWHITE_EX + "Level: " + str(data["level"]), end="")
    print(" | ", end="")
    print(Style.BRIGHT + "Experience: " + str(data["xp"]) + " / " + str(data["xp_to_next_level"]))

    print("Skills: | ", end="")
    for skill in data["skills"].keys():
        print(Style.BRIGHT + skill + ": " + str(data["skills"][skill]) + " | ", end="")
    print()

    if "goal_status" in story:
        print(Style.BRIGHT + Fore.LIGHTCYAN_EX + "Goal: " + Fore.WHITE + story["goal"])

    print_inventory(data["inventory"])

    if data["story"]["scene"]:
        bold_divider()
        print(action_res_message + Style.BRIGHT + Fore.WHITE + data["story"]["scene"])
        bold_divider()
    print()


def show_general_status(data, shopkeeper_recommendation="", shopkeeper_description=""):
    print_background(data["background"])
    print(Style.BRIGHT + Fore.YELLOW + "Coins: " + str(data["coins"]))
    print_inventory(data["inventory"])
    if shopkeeper_recommendation != "":
        print(
            Style.BRIGHT + Fore.LIGHTCYAN_EX + shopkeeper_description + ":" + Style.NORMAL + Fore.WHITE + " \"" + shopkeeper_recommendation + "\"")


def get_save_status(content):
    if len(content["story"]) > 0:
        if len(content["story"]["options"]) == 0 or (
                "goal_status" in content["story"] and content["story"]["goal_status"] != "in progress"):
            return "complete"
        return "active"
    return "none"


def exit_game():
    print("Saving and quitting..")
    exit()


# ------------------------------------------- #
# ---------------- Sequences ---------------- #
# ------------------------------------------- #


def choose_save_sequence():
    save = ""

    while save == "":
        save_list = req("/saves_list")
        if save_list["status"] == "error":
            print_error(save_list["reason"])
            return None
        save_list = save_list["result"]

        extras = ["(*) New save", "(*) Delete a Save", "(*) Logout", "(*) Exit"]
        if len(save_list) == 0:
            extras.remove("(*) Delete a Save")
        choice = choose_from_list("Welcome!\nPlease select a save file:", save_list + extras)

        if choice == len(save_list):  # New save
            clear_screen()
            generate_title()
            save = new_save_sequence()
        elif choice == len(save_list) + 1 and len(save_list) > 0:  # Delete save
            clear_screen()
            generate_title()
            delete_save_sequence(save_list)
        elif choice == len(save_list) + 2 or (choice == len(save_list) + 1 and len(save_list) == 0):  # Logout
            logout()
            clear_screen()
            return None
        elif choice == len(save_list) + 3 or (choice == len(save_list) + 2 and len(save_list) == 0):  # Exit
            exit_game()
        else:  # Load save
            save = save_list[choice]

    return save


def new_save_sequence():
    background = {}

    available_themes = req("/themes")
    if available_themes["status"] == "error":
        print_error(available_themes["reason"])
        return ""
    available_themes = available_themes["result"]

    choice = choose_from_list("Choose a theme:", list(available_themes.keys()))
    theme = available_themes[list(available_themes.keys())[choice]]

    for field in theme["fields"].keys():
        field_values = theme["fields"][field]
        if isinstance(field_values, list):
            choice = choose_from_list("Choose a " + field + ":", field_values)
            background[field] = field_values[choice]
        else:
            if field != "details":
                background[field] = input_prompt("Choose a " + field + ": ", lambda x: len(x) <= 20, "Too long!")

    for extra_field in theme["extra_fields"]:
        if background[extra_field["field"]] in extra_field["value"]:
            if isinstance(extra_field["extra_field_value"], list):
                choice = choose_from_list("Choose a " + extra_field["extra_field"] + ":",
                                          extra_field["extra_field_value"])
                background[extra_field["extra_field"]] = extra_field["extra_field_value"][choice]
            elif extra_field["extra_field_value"] == "freetext":
                background[extra_field["extra_field"]] = input_prompt("Choose a " + extra_field["extra_field"] + ": ",
                                                                      lambda x: len(x) <= 20, "Too long!")

    background["details"] = input_prompt("Provide some short general info about your character: ",
                                         lambda x: len(x) <= 120, "Too long!")

    result = req("/new_save", {"theme": theme["name"], "background": background})
    if result["status"] == "error":
        print_error(result["reason"])
        return ""
    return result["result"]


def delete_save_sequence(saves_list):
    result = {"status": "error"}
    while result["status"] == "error":
        choice = choose_from_list("Please select a save file to delete:", saves_list + ["Go Back"])
        if choice != len(saves_list):
            result = req("/delete", {"save_name": saves_list[choice]})
            if result["status"] == "error":
                print_error(result["reason"])
    clear_screen()
    generate_title()


def no_story_sequence(save_name, player_data, gen_img=True):
    if player_data["death"]:
        print("You Died!")
        print("This character will be deleted. Press any key to continue...")
        input()
        result = req("/delete", {"save_name": save_name})
        if result["status"] == "error":
            print_error(result["reason"])
        exit_game()
    else:
        show_general_status(player_data)
        print()
        choice = choose_from_list("What would you like to do?", ["Start a new story", "Shop for items", "Exit"])
        if choice == 0:
            new_story_sequence(save_name)
        elif choice == 1:
            clear_screen()
            show_general_status(player_data)
            print()
            shop_sequence(save_name, gen_img)
        elif choice == 2:
            exit_game()


def new_story_sequence(save_name):
    answer = yes_no_input("Do you want the adventure to have a set goal?")
    goal = None
    regen = False
    if answer:
        while goal is None:
            print()
            proccess_print("Generating goals...")
            result = req("/goals", {"regen": regen, "save_name": save_name})

            clear_line()
            if result["status"] == "error":
                print_error(result["reason"])
                print("Press Enter to try again...", end="")
                input()
                continue
            goals = {goal["goal"]: {"xp_reward": goal["xp_reward"], "gold_reward": goal["gold_reward"]} for goal in
                     result["result"]}
            regen = False

            def goal_description(goal):
                if goal.startswith("(*)"):
                    return "Not a goal"
                goal_text = ""
                if goals[goal]["gold_reward"] > 0:
                    goal_text += Fore.YELLOW + str(goals[goal]["gold_reward"]) + " coins" + Fore.WHITE + ", "
                goal_text += Fore.LIGHTCYAN_EX + str(goals[goal]["xp_reward"]) + " XP"
                return goal_text

            choice = choose_from_list("Choose a goal:", list(goals.keys()) + ["(*) Custom Goal",
                                                                              "(*) Regenerate goals"],
                                      preview_func=goal_description, preview_title="Goal Reward")

            if choice == len(goals):  # Custom goal
                goal = input_prompt("Write your own goal (type 'x' to cancel): ")
                if goal == "x" or goal == "X":
                    clear_line(len(goals) + 4)
                    goal = None
                    continue
            elif choice == len(goals) + 1:  # Regenerate goals
                clear_line(len(goals) + 4)
                regen = True
                continue
            else:  # Goal chosen
                goal = result["result"][choice]["goal"]

        result = req("/new_story", {"goal": goal, "save_name": save_name})
    else:
        result = req("/new_story", {"save_name": save_name})

    clear_screen()
    if result["status"] == "error":
        print_error(result["reason"])


def shop_sequence(save_name, gen_img):
    def get_shop_sequence():
        while True:
            proccess_print("Entering shop...")
            shop_result = req("/shop", {"save_name": save_name})
            if shop_result["status"] == "error":
                print_error(shop_result["reason"])
                print("Press Enter to try again...", end="")
                input()
                clear_screen()
            else:
                clear_screen()
                return shop_result["result"]

    img = gen_img
    screen = "shop"

    while True:
        # Refresh shop
        clear_screen()
        shop = get_shop_sequence()
        if img:
            show_image(save_name)
            img = False

        shopkeeper_description = shop["shopkeeper_description"]
        shopkeeper_recommendation = shop["shopkeeper_recommendation"]
        player_data = req("/fetch", {"save_name": save_name})
        if player_data["status"] == "error":
            print_error(player_data["reason"])
            exit_game()
        player_data = player_data["result"]
        show_general_status(player_data, shopkeeper_recommendation, shopkeeper_description)
        print()

        if shopkeeper_description == "No shopkeeper available":
            print("Press Enter to go back...", end="")
            input()
            break

        sold_items = shop["sold_items"]
        buy_items = shop["buy_items"]

        # Shopkeeper screen
        if screen == "shop":
            choice = choose_from_list(shopkeeper_description + ": \"What would you like to do?\"", ["Buy", "Sell", "Exit Shop"])
            if choice == 0:
                screen = "buy"
                continue
            elif choice == 1:
                screen = "sell"
                continue
            elif choice == 2:
                clear_screen()
                break

        # Buy screen
        elif screen == "buy":
            if len(sold_items) == 0:
                print(shopkeeper_description + ": \"I have nothing to sell you!\"")
                print("Press Enter to go back...", end="")
                input()
                screen = "shop"
                continue

            result = {"status": "error"}
            while result["status"] == "error":
                def shop_item_description(item):
                    if item.startswith("(*)"):
                        return "Go Back"
                    return Style.BRIGHT + item + Style.DIM + " | " + sold_items[item][
                        0] + " | " + Style.BRIGHT + Fore.YELLOW + str(sold_items[item][1]) + " coins"

                choice = choose_from_list(shopkeeper_description + ": \"What would you like to buy?\"",
                                          list(sold_items.keys()) + ["(*) Go Back"],
                                          preview_func=shop_item_description, preview_title="Item Description")
                if choice == len(sold_items):
                    screen = "shop"
                    result = {"status": "success"}
                    clear_screen()
                    continue

                result = req("/buy", {"save_name": save_name, "item_name": list(sold_items.keys())[choice]})
                if result["status"] == "error":
                    print_error(shopkeeper_description + ": \"" + result["reason"] + "\"")
                    continue

        elif screen == "sell":
            if len(buy_items) == 0:
                print(shopkeeper_description + ": \"I don't want to buy anything from you!\"")
                print("Press Enter to go back...", end="")
                input()
                screen = "shop"
                continue

            result = {"status": "error"}
            while result["status"] == "error":
                def shop_item_description(item):
                    if item.startswith("(*)"):
                        return "Go Back"
                    return Style.BRIGHT + item + Style.DIM + " | " + buy_items[item][
                        0] + " | " + Style.BRIGHT + Fore.YELLOW + str(buy_items[item][1]) + " coins"

                choice = choose_from_list(shopkeeper_description + ": \"What would you like to sell?\"",
                                          list(buy_items.keys()) + ["(*) Go Back"],
                                          preview_func=shop_item_description, preview_title="Item Description")
                if choice == len(buy_items):
                    screen = "shop"
                    result = {"status": "success"}
                    clear_screen()
                    continue

                result = req("/sell", {"item_name": list(buy_items.keys())[choice], "save_name": save_name})
                if result["status"] == "error":
                    print_error(shopkeeper_description + ": \"" + result["reason"] + "\"")


def leveled_up_sequence(save_name, skills, points):
    print(Style.BRIGHT + Fore.LIGHTCYAN_EX + "|----------------------------|")
    print(Style.BRIGHT + Fore.LIGHTCYAN_EX + "|--- You have Leveled Up! ---|")
    print(Style.BRIGHT + Fore.LIGHTCYAN_EX + "|----------------------------|\n")
    choice = choose_from_list(f"You have {points} skill points. Which skill would you like to improve?", skills)
    result = req("/spend", {"save_name": save_name ,"skill": skills[choice]})
    if result["status"] == "error":
        print_error(result["reason"])


def add_option_sequence(save_name) -> None:
    new_option = ""
    while new_option == "":
        new_option = input_prompt("Write your own option (type 'x' to cancel): ")
        if new_option == "x" or new_option == "'x'":
            return
        result = req("/new_option", {"new_action": new_option, "save_name": save_name})

        if result["status"] == "error":
            print_error(result["reason"])
            new_option = ""
            continue


def game_step_sequence(save_name, game_data, action_res_message, gen_img=True):
    show_story_status(game_data, action_res_message)

    while game_data["action_points"] >= 1:
        leveled_up_sequence(save_name, list(game_data["skills"].keys()), game_data["action_points"])
        clear_screen()
        load = req("/fetch", {"save_name": save_name})
        if load["status"] == "error":
            print_error(load["reason"])
            exit_game()
        game_data = load["result"]
        show_story_status(game_data, action_res_message)

    def option_description(option):
        if option.startswith("(*)"):
            return "Save and Quit"
        idx = game_data["story"]["options"].index(option)

        proccessed_option = Style.BRIGHT + "Success Rate: " + Style.NORMAL + str(
            game_data["story"]["rates"][idx] * 100) + "%"
        adv_rate = game_data["story"]["rates"][idx] + (1 - game_data["story"]["rates"][idx]) * 0.75
        color = ""
        if game_data["skills"][game_data["story"]["advantages"][idx]] >= game_data["story"]["levels"][idx]:
            color = Fore.GREEN
        if game_data["story"]["rates"][idx] != 1:
            proccessed_option += Style.DIM + color + " (" + str(adv_rate * 100) + "% with " + \
                                 game_data["story"]["advantages"][idx] + ": " + str(
                game_data["story"]["levels"][idx]) + ")"

        proccessed_option += "\n" + Style.BRIGHT + "Reward XP: " + Style.NORMAL + str(
            game_data["story"]["experience"][idx])

        return proccessed_option

    if action_res_message.startswith("error"):
        print_error(action_res_message)

    choice = choose_from_list("What Will You Do?", game_data["story"]["options"] + ["(*) Add new option",
                                                                                    "(*) Abandon Story",
                                                                                    "(*) Save and Quit"],
                              preview_func=option_description, preview_title="Option Details")
    if choice == len(game_data["story"]["options"]):  # add new option
        add_option_sequence(save_name)
        return action_res_message
    if choice == len(game_data["story"]["options"]) + 1:  # abandon story
        result = req("/end_story", {"save_name": save_name})
        clear_screen()
        if result["status"] == "error":
            print_error(result["reason"])
            return action_res_message
        else:
            return Style.BRIGHT + Fore.GREEN + "[ Success! ] " + Style.RESET_ALL
    if choice == len(game_data["story"]["options"]) + 2:  # save and quit
        exit_game()

    proccess_print("Advancing story...")
    res = req("/advance", {"action": game_data["story"]["options"][choice], "save_name": save_name})
    if res["status"] == "error":
        print_error(res["reason"])
        return action_res_message
    clear_screen()

    if gen_img:
        show_image(save_name)

    action_res_message = res["result"]
    if action_res_message == "Success":
        return Style.BRIGHT + Fore.GREEN + "[ Success! +" + str(
            game_data["story"]["experience"][choice]) + "XP ] " + Style.RESET_ALL
    else:
        return Style.BRIGHT + Fore.RED + "[ Failure! ] " + Style.RESET_ALL


def game_end_sequence(save_name, data, action_res_message):
    show_story_status(data, action_res_message)

    if data["story"]["health"] <= 0:
        print(Style.BRIGHT + Fore.RED + "You Died!")
    elif "goal_status" in data["story"] and data["story"]["goal_status"] == "win":
        end_message = Style.BRIGHT + Fore.GREEN + "You Have completed your goal! "
        if data["story"]["gold_reward"] > 0:
            end_message += Fore.YELLOW + "[ +" + str(data["story"]["gold_reward"]) + " coins ] "
        if data["story"]["xp_reward"] > 0:
            end_message += Fore.LIGHTCYAN_EX + "[ +" + str(data["story"]["xp_reward"]) + " XP ]"
        print(end_message)
    elif "goal_status" in data["story"] and data["story"]["goal_status"] == "lose":
        print(Style.BRIGHT + Fore.RED + "You Have failed your quest!")
    else:
        print(Style.BRIGHT + "Game Has Ended!")

    print("Press Enter to continue...", end="")
    input()
    proccess_print("Saving progress...")
    result = req("/end_story", {"save_name": save_name})
    clear_screen()
    if result["status"] == "error":
        print_error(result["reason"])


def test_systems_sequence():
    print('Game loading...')
    status = req("/startup")

    if status["status"] == "error":
        print_error(status["reason"])
        exit()
    status = status["result"]

    if status:
        print_error(
            "The following system failed to load: " + ", ".join(status))
        if "LLM" in status:
            exit()

    clear_screen()
    return "T2I" not in status


def title_sequence(check_im):
    generate_title()
    images_toggle = False
    if check_im:
        images_toggle = yes_no_input("Do you want to generate images? (May take longer)")
        clear_line()

    save = None
    while not save:
        # Check if the user is logged in
        if TOKEN["access_token"] == "":
            with open(".env", "r") as f:
                for line in f:
                    if "ACCESS_TOKEN" in line:
                        TOKEN["access_token"] = line.split("=")[1].strip()
                        break
        login_status = TOKEN["access_token"] != ""

        if not login_status:
            login_sequence()
            clear_screen()
            generate_title()

        save = choose_save_sequence()
        clear_screen()
        generate_title()

    return save, images_toggle


def login_sequence():
    print("Welcome to the game!"
          "\nYou are not logged in.\n")
    choice = choose_from_list("What would you like to do?", ["Login", "Register", "Exit"])
    if choice == 0:
        while True:
            username = input_prompt("Username: ")
            password = input_prompt("Password: ", secret=True)
            result = req("/login", body={"username": username, "password": password})
            if result["status"] == "error":
                print_error(result["reason"])
                continue
            TOKEN["access_token"] = result["result"]
            # save the token locally
            with open(".env", "a") as f:
                f.write("\nACCESS_TOKEN=" + str(TOKEN["access_token"]))
            break
        return result["result"]
    elif choice == 1:
        while True:
            username = input_prompt("Username: ")
            password = input_prompt("Password: ", secret=True)
            result = req("/register", body={"username": username, "password": password})
            if result["status"] == "error":
                print_error(result["reason"])
                continue
            else:
                result = req("/login", body={"username": username, "password": password})
                if result["status"] == "error":
                    print_error(result["reason"])
                    continue
                TOKEN["access_token"] = result["result"]
                # save the token locally
                with open(".env", "a") as f:
                    f.write("\nACCESS_TOKEN=" + TOKEN["access_token"])
            break
        return result["result"]
    elif choice == 2:
        exit_game()


# ------------------------------------------- #
# ---------------- Main Loop ---------------- #
# ------------------------------------------- #


def game_loop(save, images_toggle):
    action_res_message = ""

    while True:
        game_data = req("/load", {"save_name": save})
        if game_data["status"] == "error":
            print_error(game_data["reason"])
            exit_game()
        game_data = game_data["result"]

        status = get_save_status(game_data)
        if status == "none":
            no_story_sequence(save, game_data, images_toggle)
        elif status == "complete":
            game_end_sequence(save, game_data, action_res_message)
        elif status == "active":
            action_res_message = game_step_sequence(save, game_data, action_res_message, images_toggle)
        else:
            print_error("Invalid save status!")
            exit()


def start():
    check_images = test_systems_sequence()
    save = None
    images_toggle = False
    while not save:
        save, images_toggle = title_sequence(check_images)
    TOKEN["gen_img"] = images_toggle

    game_loop(save, images_toggle)
