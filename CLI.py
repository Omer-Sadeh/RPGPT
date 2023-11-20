import itertools
import time
from backend.API import *
from backend.Themes import Available_Themes
from backend.Utility import start_promise, await_promise
from PIL import Image
from colorama import init, Fore, Back, Style
from dotenv import load_dotenv
from simple_term_menu import TerminalMenu
load_dotenv()
init(autoreset=True)


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
            return chr(num+96)
        
    menu_options = ["[" + shortcut(idx+1) + "] " + str(option) for idx, option in enumerate(options)]
    
    terminal_menu = TerminalMenu(menu_options, title=prompt+"\n", skip_empty_entries=True,
                                 preview_command=preview_func, preview_title=preview_title,
                                menu_highlight_style=("bold","fg_cyan"), menu_cursor_style=("bold","fg_cyan"),
                                shortcut_key_highlight_style=("bold","fg_cyan"))
    choice = terminal_menu.show()
    
    chosen = options[choice]
    print(Style.BRIGHT + "Option chosen: " + Fore.LIGHTWHITE_EX + str(chosen) + "\n")
    
    return choice


def input_prompt(prompt, check_func=lambda _: True, error="Invalid input!"):
    print(Style.BRIGHT + prompt + Style.NORMAL, end="")
    answer = input()
    if not check_func(answer):
        invalid_choice(error)
        return input_prompt(prompt, check_func, error)
    return answer


def invalid_choice(error="Invalid choice!"):
    print()
    print(Fore.RED + error + " Please try again.")
    print()


def proccess_print(text):
    print(Style.DIM + text)


def show_image(image_location):
    image = Image.open(image_location)
    image.show()
    return True


def yes_no_input(prompt):
    answer = input_prompt(prompt + " (Y/N): ")
    if answer.lower() == "y" or answer.lower() == "yes":
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


def print_inventory(inventory: Inventory):
    print("----- " + Style.BRIGHT + "Inventory" + Style.NORMAL + " -----")
    for category in inventory.categories:
        print(Style.BRIGHT + category + " |" + Style.NORMAL, end="")
        for item in inventory[category]:
            print(" ( " + item + " )", end="")
        print()
    print("---------------------")
    

def print_background(background):
    divider(False)
    if "traits" in background:
        print(Style.BRIGHT + background["name"] + Style.NORMAL +  " (" + ", ".join(background["traits"]) + ")" , end="")
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


def choose_save_sequence():
    save = ""
    
    while save == "":
        save_list = get_saves_list()
        if save_list["status"] == "error":
            print_error(save_list["reason"])
            exit()
        save_list = save_list["result"]
        
        extras = ["(*) New save", "(*) Delete a Save", "(*) Exit"]
        if len(save_list) == 0:
            extras.remove("(*) Delete a Save")
        choice = choose_from_list("Please select a save file:", save_list + extras)
        
        if choice == len(save_list):
            clear_screen()
            generate_title()
            save = new_save_sequence(save_list)
        elif choice == len(save_list) + 1 and len(save_list) > 0:
            clear_screen()
            generate_title()
            delete_save_sequence(save_list)
        elif choice == len(save_list) + 2 or (choice == len(save_list) + 1 and len(save_list) == 0):
            exit_game()
        else:
            save = save_list[choice]
            
    return save


def new_save_sequence(save_list):
    background = {}
    
    choice = choose_from_list("Choose a theme:", Available_Themes)
    theme = Available_Themes[choice]
    
    for field in theme.get_fields():
        field_values = theme.get_field_options(field)
        if type(field_values) == list:
            choice = choose_from_list("Choose a " + field + ":", field_values)
            background[field] = field_values[choice]
        else:
            background[field] = input_prompt("Choose a " + field + ": ", lambda x: len(x) <= 20, "Too long!")
        
    background["name"] = input_prompt("Character name: ", lambda x: len(x) <= 20, "Name too long!")
    print()
    
    for extra_field in theme.extra_fields:
        if background[extra_field["field"]] in extra_field["value"]:
            if type(extra_field["extra_field_value"]) == list:
                choice = choose_from_list("Choose a " + extra_field["extra_field"] + ":", extra_field["extra_field_value"])
                background[extra_field["extra_field"]] = extra_field["extra_field_value"][choice]
            else:
                background[extra_field["extra_field"]] = input_prompt("Choose a " + extra_field["extra_field"] + ": ", lambda x: len(x) <= 20, "Too long!")
            print()
    
    inventory = theme.generate_empty_inventory(background)
    backstory = ""
    traits = []
    while backstory == "":
        answer = yes_no_input("Do you want to auto-generate the character's backstory?")
        if answer:
            print()
            proccess_print("Generating backstory...")
            result = generate_backstory(theme, background)
            clear_line(2)
            if result["status"] == "error":
                print_error(result["reason"])
                print("Press Enter to try again...", end="")
                input()
                continue
            backstory = result["result"]["backstory"]
            inventory = result["result"]["inventory"]
            traits = result["result"]["traits"]
            print(Style.BRIGHT + "\nGenerated backstory: \n" + Style.NORMAL + backstory)
            print(Style.BRIGHT + "\nGenerated traits: \n" + Style.NORMAL + ", ".join(traits))
            print(Style.BRIGHT + "\nGenerated inventory:" + Style.NORMAL)
            print_inventory(inventory)
            answer = yes_no_input("\nDo you want this backstory?")
            if not answer:
                clear_line(len(inventory.categories)+14)
                backstory = ""
                inventory = theme.generate_empty_inventory(background)
        else:
            clear_line()
            backstory = input_prompt("Write your own backstory: ")
    background["backstory"] = backstory
    if traits != []:
        background["traits"] = traits
    
    print()
    save_name = input_prompt("Save name: ", lambda x: x not in save_list, "Save name already exists!")
    print()
    
    result = new_save(save_name, theme, background, inventory)
    if result["status"] == "error":
        print_error(result["reason"])
        return ""
    return save_name


def delete_save_sequence(saves_list):
    result = {"status": "error"}
    while result["status"] == "error":
        choice = choose_from_list("Please select a save file to delete:", saves_list + ["Go Back"])
        if choice != len(saves_list):
            result = delete_save(saves_list[choice])
            if result["status"] == "error":
                print_error(result["reason"])
    clear_screen()
    generate_title()


def no_story_sequence(save_name, player_data, goals_promise, shop_promise, gen_img=True):
    if player_data["death"]:
        print("You Died!")
        print("This character will be deleted. Press any key to continue...")
        input()
        result = delete_save(save_name)
        if result["status"] == "error":
            print_error(result["reason"])
        exit_game()
    else:
        show_general_status(player_data)
        print()
        choice = choose_from_list("What would you like to do?", ["Start a new story", "Shop for items", "Exit"])
        if choice == 0:
            new_story_sequence(save_name, player_data, goals_promise)
        elif choice == 1:
            clear_screen()
            show_general_status(player_data)
            print()
            shop_sequence(save_name, shop_promise, gen_img)
            goals_promise = start_promise(generate_goals, save_name)
        elif choice == 2:
            exit_game()
  

def new_story_sequence(save_name, player_data, goals_promise):
    answer = yes_no_input("Do you want the adventure to have a set goal?")
    goal = None
    result = {}
    if answer:
        while goal == None:
            print()
            proccess_print("Generating goals...")
            if result == {}:
                result = await_promise(goals_promise)
            else:
                result = generate_goals(save_name)
            clear_line()
            if result["status"] == "error":
                print_error(result["reason"])
                print("Press Enter to try again...", end="")
                input()
                continue
            goals = {goal["goal"]: {"xp_reward": goal["xp_reward"], "gold_reward": goal["gold_reward"]} for goal in result["result"]}
            
            def goal_description(goal):
                if goal.startswith("(*)"):
                    return "Not a goal"
                goal_text = ""
                if goals[goal]["gold_reward"] > 0:
                    goal_text += Fore.YELLOW + str(goals[goal]["gold_reward"]) + " coins" + Fore.WHITE + ", "
                goal_text += Fore.LIGHTCYAN_EX + str(goals[goal]["xp_reward"]) + " XP"
                return goal_text
            
            choice = choose_from_list("Choose a goal:", list(goals.keys()) + ["(*) Regenerate goals", "(*) Write your own goal (no reward)"],
                                        preview_func=goal_description, preview_title="Goal Reward")
            
            if choice == len(goals):
                clear_line(len(goals) + 3)
                continue
            elif choice == len(goals) + 1:
                clear_line(len(goals) + 2)
                goal_text = input_prompt("Write your own goal: ")
                goal = {"goal": goal_text, "gold_reward": 0, "xp_reward": 0}
            else:
                goal = result["result"][choice]
                
        result = new_story(save_name, goal, player_data["inventory"])
        
    clear_screen()
    if result["status"] == "error":
        print_error(result["reason"])
        
          
def shop_sequence(save_name, shop_promise, gen_img):
    proccess_print("Entering shop...")
    result = await_promise(shop_promise)
    if result["status"] == "error":
        print_error(result["reason"])
        print("Press Enter to try again...", end="")
        input()
        shop_promise = start_promise(generate_shop, save_name, gen_img)
        clear_screen()
        return
    shop = result["result"]
    
    if gen_img:
        show_image("saves/" + save_name + ".png")
    
    shopkeeper_recommendation = shop["shopkeeper_recommendation"]
    sold_items = shop["sold_items"]
    buy_items = shop["buy_items"]
    screen = "shop"
    
    while True:
        clear_screen()
        player_data = load_save(save_name)
        if player_data["status"] == "error":
            print_error(player_data["reason"])
            exit_game()
        show_general_status(player_data["result"], shopkeeper_recommendation)
        print()
        
        if screen == "shop":
            choice = choose_from_list("Shopkeeper: \"What would you like to do?\"", ["Buy", "Sell", "Exit Shop"])
            if choice == 0:
                screen = "buy"
                continue
            elif choice == 1:
                screen = "sell"
                continue
            elif choice == 2:
                clear_screen()
                break
            
        elif screen == "buy":
            if len(sold_items) == 0:
                print("Shopkeeper: \"I have nothing to sell you!\"")
                print("Press Enter to go back...", end="")
                input()
                screen = "shop"
                continue
            
            result = {"status": "error"}
            while result["status"] == "error":
                def shop_item_description(item):
                    if item.startswith("(*)"):
                        return "Go Back"
                    return Style.BRIGHT + item + Style.DIM + " | " + sold_items[item][0] + " | " + Style.BRIGHT + Fore.YELLOW + str(sold_items[item][1]) + " coins"
                choice = choose_from_list("Shopkeeper: \"What would you like to buy?\"", list(sold_items.keys()) + ["(*) Go Back"],
                                          preview_func=shop_item_description, preview_title="Item Description")
                if choice == len(sold_items):
                    screen = "shop"
                    result = {"status": "success"}
                    clear_screen()
                    continue
                
                item = list(sold_items.keys())[choice]
                category = sold_items[item][0]
                price = sold_items[item][1]
                
                if player_data["result"]["coins"] < price:
                    print(Style.BRIGHT + Fore.LIGHTCYAN_EX + "Shopkeeper" + Style.NORMAL + Fore.WHITE + ": \"You don't have enough coins!\"")
                    continue
                result = buy_item(save_name, item, category, price)
                if result["status"] == "error":
                    print_error(result["reason"])
            
                buy_items[item] = sold_items[item]
                sold_items.pop(item)
                shopkeeper_recommendation = "Shopkeeper: \"Thank you for your purchase!\""
        
        elif screen == "sell":
            if len(buy_items) == 0:
                print("Shopkeeper: \"I don't want to buy anything from you!\"")
                print("Press Enter to go back...", end="")
                input()
                screen = "shop"
                continue
            
            result = {"status": "error"}
            while result["status"] == "error":
                def shop_item_description(item):
                    if item.startswith("(*)"):
                        return "Go Back"
                    return Style.BRIGHT + item + Style.DIM + " | " + buy_items[item][0] + " | " + Style.BRIGHT + Fore.YELLOW + str(buy_items[item][1]) + " coins"
                choice = choose_from_list("Shopkeeper: \"What would you like to sell?\"", list(buy_items.keys()) + ["(*) Go Back"],
                                          preview_func=shop_item_description, preview_title="Item Description")
                if choice == len(buy_items):
                    screen = "shop"
                    result = {"status": "success"}
                    clear_screen()
                    continue
                
                item = list(buy_items.keys())[choice]
                category = buy_items[item][0]
                price = buy_items[item][1]
                
                result = sell_item(save_name, item, category, price)
                if result["status"] == "error":
                    print_error("Shopkeeper: \"" + result["reason"] + "\"")
            
                sold_items[item] = buy_items[item]
                buy_items.pop(item)
                shopkeeper_recommendation = "Shopkeeper: \"Thank you, that would sell great!\""


def show_story_status(data, action_res_message):
    print_background(data["background"])
    story = data["story"]
    print(Style.BRIGHT + Fore.RED + "Health: " + str(story["health"]), end="")
    print(" | ", end="")
    print(Style.BRIGHT + Fore.YELLOW + "Coins: " + str(story["coins"]), end="")
    print(" | ", end="")
    print(Style.BRIGHT + Fore.LIGHTWHITE_EX + "Level: " + str(data["level"]), end="")
    print(" | ", end="")
    print(Style.BRIGHT + "Experience: " + str(data["xp"]) + " / " + str(data["xp_to_next_level"]))
    
    print("Skills: | ", end="")
    for skill in data["skills"].keys():
        print(Style.BRIGHT + skill + ": " + str(data["skills"][skill]) + " | ", end="")
    print()
    
    if "goal_status" in story:
        print(Style.BRIGHT + Fore.LIGHTCYAN_EX + "Goal: " +Fore.WHITE + story["goal"])
    
    print_inventory(story["inventory"])
    
    if data["story"]["scene"]:
        bold_divider()
        print(action_res_message + Style.BRIGHT + Fore.LIGHTWHITE_EX + data["story"]["scene"])
        bold_divider()
    print()
    

def show_general_status(data, shopkeeper_recommendation=""):
    print_background(data["background"])
    print(Style.BRIGHT + Fore.YELLOW + "Coins: " + str(data["coins"]))
    print_inventory(data["inventory"])
    if shopkeeper_recommendation != "":
        print(Style.BRIGHT + Fore.LIGHTCYAN_EX + "Shopkeeper:" + Style.NORMAL + Fore.WHITE + " \"" + shopkeeper_recommendation + "\"")
    

def leveled_up_sequence(save_name, skills, points):
    print(Style.BRIGHT + Fore.LIGHTCYAN_EX + "|----------------------------|")
    print(Style.BRIGHT + Fore.LIGHTCYAN_EX + "|--- You have Leveled Up! ---|")
    print(Style.BRIGHT + Fore.LIGHTCYAN_EX + "|----------------------------|\n")
    choice = choose_from_list(f"You have {points} skill points. Which skill would you like to improve?", skills)
    result = spend_action_point(save_name, skills[choice])
    if result["status"] == "error":
        print_error(result["reason"])


def game_step_sequence(save_name, game_data, action_res_message, gen_img=True):   
    choices_promises = [start_promise(generate_result, save_name, choice) for choice in game_data["story"]["options"]]
    show_story_status(game_data, action_res_message)
        
    while game_data["action_points"] >= 1:
        leveled_up_sequence(save_name, list(game_data["skills"].keys()), game_data["action_points"])
        clear_screen()
        load = load_save(save_name)
        if load["status"] == "error":
            print_error(load["reason"])
            exit_game()
        game_data = load["result"]
        show_story_status(game_data, action_res_message)
    
    def option_description(option):
        if option.startswith("(*)"):
            return "Save and Quit"
        idx = game_data["story"]["options"].index(option)
        
        proccessed_option = Style.BRIGHT + "Success Rate: " + Style.NORMAL + str(game_data["story"]["rates"][idx]*100) + "%"
        adv_rate = game_data["story"]["rates"][idx] + (1 - game_data["story"]["rates"][idx]) * 0.75
        color = ""
        if game_data["skills"][game_data["story"]["advantages"][idx]] >= game_data["story"]["levels"][idx]:
            color = Fore.GREEN
        if game_data["story"]["rates"][idx] != 1:
            proccessed_option += Style.DIM + color + " (" + str(adv_rate*100) + "% with " + game_data["story"]["advantages"][idx] + ": " + str(game_data["story"]["levels"][idx]) + ")"
        
        proccessed_option += "\n" + Style.BRIGHT + "Reward XP: " + Style.NORMAL + str(game_data["story"]["experience"][idx])
    
        return proccessed_option
    
    res = {"status": "error"}
    while res["status"] == "error":
        choice = choose_from_list("What Will You Do?", game_data["story"]["options"] + ["(*) Save and Quit"],
                                  preview_func=option_description, preview_title="Option Details")
        if choice == len(game_data["story"]["options"]):
            exit_game()
            
        proccess_print("Advancing story...")
        
        res = await_promise(choices_promises[choice])
        if res["status"] == "error":
            proccess_print("Advancing takes longer than usual..")
            res = advance_story(save_name, game_data["story"]["options"][choice], gen_img)
            if res["status"] == "error":
                print_error(res["reason"])
                choices_promises[choice] = start_promise(generate_result, save_name, game_data["story"]["options"][choice])
        else:
            res = make_story_choice(save_name, game_data["story"]["options"][choice], res["result"], gen_img)
            if res["status"] == "error":
                print_error(res["reason"])
            
        
    clear_screen()  
    res = res["result"]
        
    if gen_img:
        show_image("saves/" + save_name + ".png")
        
    if res == "Success":
        return Style.BRIGHT + Fore.GREEN + "[ Success! +" + str(game_data["story"]["experience"][choice]) + "XP ] " + Style.RESET_ALL
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
    result = end_game(save_name)
    clear_screen()
    if result["status"] == "error":
        print_error(result["reason"])
        

def get_save_status(content):
    if len(content["story"]) > 0:
        if len(content["story"]["options"]) == 0 or ("goal_status" in content["story"] and content["story"]["goal_status"] != "in progress"):
            return "complete"
        return "active"
    return "none"


def exit_game():
    print("Saving and quitting..")
    exit()


def test_systems():
    def loading_animation():
        for c in itertools.cycle(['|', '/', '-', '\\']):
            if done:
                break
            print('\rGame loading ' + c, end="")
            time.sleep(0.15)
    
    clear_screen()
    print()
    done = False
    start_promise(loading_animation)
    status = system_status()
    done = True
    await_promise(status)
    
    if status["status"] == "error":
        print_error(status["reason"])
        exit()
    status = status["result"]
    
    if status != {}:
        print_error("The following system failed to load:\n" + "\n".join([system + ": " + status[system] for system in status]))
        exit()
        
    clear_screen()


def title_sequence():
    generate_title()
    images_toggle = yes_no_input("Do you want to generate images? (May take longer)")
    clear_line()
    save = choose_save_sequence()
    clear_screen()
    
    return save, images_toggle
 

def game_loop(save, images_toggle):
    generate_promises = True
    action_res_message = ""
    
    while True:
        game_data = load_save(save)
            
        if game_data["status"] == "error":
            print_error(game_data["reason"])
            exit_game()
        game_data = game_data["result"]
            
        status = get_save_status(game_data)
        if status == "none":
            if generate_promises:
                shop_promise = start_promise(generate_shop, save, images_toggle)
                goals_promise = start_promise(generate_goals, save)
                generate_promises = False
            no_story_sequence(save, game_data, goals_promise, shop_promise, images_toggle)
        elif status == "complete":
            game_end_sequence(save, game_data, action_res_message)
            generate_promises = True
        elif status == "active":
            action_res_message = game_step_sequence(save, game_data, action_res_message, images_toggle)
        else:
            print_error("Invalid save status!")
            exit()
               

if __name__ == "__main__":
    test_systems()
    save, images_toggle = title_sequence()
    
    game_loop(save, images_toggle)
