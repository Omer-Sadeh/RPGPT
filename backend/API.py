import ast
import random
import json
import os
import backend.models.T2I as T2I
from backend.Prompts import *
import backend.models.LLM as LLM
from backend.Utility import *
from backend.Classes import *


# ---------------- Utilities ---------------- #


@error_wrapper
def request_json(messages):
    result = LLM.generate(messages)
    if result["status"] == "success":
        try:
            json_res = ast.literal_eval(result["result"])
            return json_res
        except:
            raise Exception("Error parsing JSON.\n" + result["result"]) 
    else:
        raise Exception(result["reason"])


def load_game(save_name:str):
    with open("saves/"+save_name+".json", "r") as save_file:
        content = json.load(save_file)
        content["inventory"] = Inventory(inventory=content["inventory"])
        if "story" in content and "inventory" in content["story"]:
            content["story"]["inventory"] = Inventory(inventory=content["story"]["inventory"])
        return content


def save_game(save_name: str, data: dict):
    data["theme"] = str(data["theme"])
    data["inventory"] = data["inventory"].to_dict()
    if "story" in data and "inventory" in data["story"]:
        if isinstance(data["story"]["inventory"], Inventory):
            data["story"]["inventory"] = data["story"]["inventory"].to_dict()
    with open("saves/"+save_name+".json", "w") as save_file:
        json.dump(data, save_file, indent=2, separators=(', ', ' : '))


def probability_function(probability):
    if 0 <= probability <= 1:
        random_number = random.random()
        if random_number < probability:
            return "Success"
        else:
            return "Failure"
    else:
        raise ValueError('Probability must be between 0 and 1.')


def remove_init_num(input_string):
    try:
        if len(input_string) > 2 and input_string[0].isdigit() and input_string[1] == '.' and input_string[2] == ' ':
            return input_string[3:]
        else:
            return input_string
    except:
        print("Error: " + str(input_string))
        return input_string


def trim_history(history):
    history_limit = 20
    written_history = ""
    
    if len(history) > (history_limit * 2):
        for part in history[len(history)-(history_limit * 2):]:
            written_history += part + " "
    else:
        for part in history:
            written_history += part + " "
    
    return written_history


def calculate_success_rate(data, index):
    base_rate = data["story"]["rates"][index]
    updated_rate = base_rate
    skills = list(data["skills"].keys())
    
    if len(data["story"]["full_history"]) > 0:
        advantage_skill = data["story"]["advantages"][index]
        if advantage_skill not in skills:
            advantage_skill = skills[0]
        advantage_level = data["story"]["levels"][index]
        if data["skills"][advantage_skill] >= advantage_level:
            updated_rate += (1 - base_rate) * 0.75
    
    return updated_rate


def calc_xp_to_level(level):
    res_xp = 25 * ((level + 1) ** 2) - 50 * (level + 1)
    return res_xp if res_xp > 0 else 25


def update_xp(data, added_xp):
    current_xp = data["xp"] + added_xp
    
    while current_xp >= data["xp_to_next_level"]:
        current_xp -= data["xp_to_next_level"]
        data["level"] += 1
        data["xp_to_next_level"] = calc_xp_to_level(data["level"] + 1)
        data["action_points"] += 1
        
    data["xp"] = current_xp
    return data


def update_story(save_name, old_data, result, result_xp, new_history, new_full_history):
    story = old_data["story"]
    skills = list(old_data["skills"].keys())
    
    story["health"] = result["health"]
    story["inventory"] = result["inventory"]
    story["coins"] = result["coins"]
    story["history"] = new_history
    story["full_history"] = new_full_history
    story["scene"] = result["scene"]
    story["prompt"] = result["prompt"]
    if "options" in result:
        story["options"] = [remove_init_num(option) for option in result["options"] if option != ""]
        story["rates"] = result["rates"]
        story["advantages"] = [skill if skill in skills else "INT" for skill in result["advantages"]]
        story["levels"] = result["level"]
        story["experience"] = result["experience"]
    else:
        story["options"] = []
    if story["goal"]:
        if result["goal_status"] == "in_progress":
            story["goal_status"] = "in progress"
        story["goal_status"] = result["goal_status"]
    if "new_backstory" in result:
        story["new_backstory"] = result["new_backstory"]
    old_data["story"] = story
    
    save_game(save_name, update_xp(old_data, result_xp))


# ---------------- API ---------------- #


@error_wrapper
def system_status():
    test_llm_promise = start_promise(LLM.generate, [{"role": "system", "content": "status"}])
    test_t2i_promise = start_promise(T2I.generate, "test", "test.png")
    test_llm = await_promise(test_llm_promise)
    test_t2i = await_promise(test_t2i_promise)
    result ={}
    if test_llm["status"] == "error":
        result["LLM"] = test_llm["reason"]
    if test_t2i["status"] == "error":
        result["T2I"] = test_t2i["reason"]
    if os.path.isfile("test.png"):
        os.remove("test.png")
    if not os.path.isdir("saves"):
        os.mkdir("saves")
    
    return result


@error_wrapper
def get_saves_list():
    return [os.path.splitext(f)[0] for f in os.listdir("saves") if os.path.isfile(os.path.join("saves", f)) and f.endswith('.json')]


@error_wrapper
def load_save(save_name:str):
    return load_game(save_name)


@error_wrapper
def new_save(save_name: str, theme: Theme, background: dict, inventory: Inventory):
    save_game(save_name, {
        "story": {},
        "theme": theme,
        "background": background,
        "level": 1,
        "xp": 0,
        "xp_to_next_level": calc_xp_to_level(1),
        "action_points": 0,
        "skills": {skill: 1 for skill in theme.skills},
        "inventory": inventory,
        "coins": 100,
        "death": False
    })
        
   
@error_wrapper     
def delete_save(save_name: str):
    os.remove("saves/"+save_name+".json")
    # remove the image only if exists
    if os.path.isfile("saves/"+save_name+".png"):
        os.remove("saves/"+save_name+".png")


@error_wrapper
def generate_goals(save_name: str):
    player_data = load_game(save_name)
    
    goal_generator_input = {
        "inventory": player_data["inventory"],
        "background": player_data["background"]
    }
    
    result = request_json([{"role": "system", "content": get_goals_generator(player_data["theme"])},
                             {"role": "user", "content": str(goal_generator_input)}])
    
    if result["status"] == "success":
        result = result["result"]
        for idx, goal in enumerate(result):
            if "gold_reward" not in goal:
                result[idx]["gold_reward"] = 0
        return result
    else:
        raise Exception(result["reason"])


@error_wrapper
def generate_backstory(theme: Theme, background: dict):
    backstory_generator_input = {
        "inventory": Inventory(),
        "background": background
    }
    
    result = request_json([{"role": "system", "content": get_backstory_generator(theme)},
                             {"role": "user", "content": str(backstory_generator_input)}])
    
    if result["status"] == "success":
        result = result["result"]
        result["inventory"] = Inventory(result["inventory"])
        return result
    else:
        raise Exception(result["reason"])
    

@error_wrapper
def new_story(save_name: str, goal: dict, inventory: Inventory):
    content = load_game(save_name)
    skills = list(content["skills"].keys())
    
    content["story"] = {
        "full_history": [],
        "history": "",
        "scene": "",
        "prompt": "",
        "img": "",
        "goal": goal["goal"] if goal else "",
        "health": 5,
        "inventory": inventory,
        "coins": content["coins"],
        "options": ["Wake up", "Look around", "Stand up"],
        "rates": [1, 1, 1],
        "advantages": [skills[0], skills[1], skills[2]],
        "levels": [0, 0, 0],
        "experience": [0, 0, 0]
    }
    if goal:
        content["story"]["goal_status"] = "in progress"
        content["story"]["gold_reward"] = goal["gold_reward"]
        content["story"]["xp_reward"] = goal["xp_reward"]
    
    save_game(save_name, content)
       

@error_wrapper
def advance_story(save_name: str, action: str, gen_img: bool=True):
    result = generate_result(save_name, action)
    if result["status"] == "error":
        raise result["reason"]
    
    result = result["result"]
    
    res = make_story_choice(save_name, action, result, gen_img)
    if res["status"] == "error":
        raise res["reason"]
    
    return result["action_result"]


@error_wrapper
def generate_result(save_name: str, action: str):
    player_data = load_game(save_name)
    story_data = player_data["story"]
    
    action_index = story_data["options"].index(action)
    
    success_rate = calculate_success_rate(player_data, action_index)
    action_result = probability_function(success_rate)
    
    action_json = {
        "history": story_data["history"],
        "choice": action,
        "result": action_result,
        "health": story_data["health"],
        "inventory": story_data["inventory"],
        "coins": story_data["coins"]
        }
    
    result = request_json([{"role": "system", "content": get_storyteller(player_data)},
                            {"role": "user", "content": str(action_json)}])
    if result["status"] == "error":
        raise result["reason"]
    
    result = result["result"]
    result["action_result"] = action_result
    return result


@error_wrapper
def make_story_choice(save_name: str, action: str, result: dict, gen_img: bool=True):
    player_data = load_game(save_name)
    story_data = player_data["story"]
    result["inventory"] = Inventory(result["inventory"])
    history = story_data["full_history"] + [action + ".", result["scene"]]
    action_index = story_data["options"].index(action)

    img = ""
    if gen_img:
        img = T2I.generate(result["prompt"], "saves/"+save_name+".png")
        if img["status"] == "error":
            raise Exception(img["reason"])
    
    result_xp = 0 if result["action_result"] == "Failure" else story_data["experience"][action_index]
    update_story(save_name, player_data, result, result_xp, trim_history(history), history)
    return result["action_result"]


@error_wrapper
def spend_action_point(save_name: str, skill: str):
    player_data = load_game(save_name)
    player_data["action_points"] -= 1
    player_data["skills"][skill] += 1
    save_game(save_name, player_data)


@error_wrapper
def generate_shop(save_name: str, gen_img: bool=True):
    player_data = load_game(save_name)
    
    shop_generator_input = {
        "inventory": player_data["inventory"],
        "background": player_data["background"]
    }
    
    result = request_json([{"role": "system", "content": get_shop_generator(player_data["theme"])},
                             {"role": "user", "content": str(shop_generator_input)}])
    
    if result["status"] == "success":
        if gen_img:
            img = T2I.generate(result["result"]["prompt"], "saves/"+save_name+".png")
            if img["status"] == "error":
                raise Exception(img["reason"])
        return result["result"]
    else:
        raise Exception(result["reason"])


@error_wrapper
def buy_item(save_name: str, item: str, category: str, price: int):
    player_data = load_game(save_name)
    
    if player_data["coins"] < price:
        raise Exception("Not enough coins.")
    if player_data["inventory"].contains(item, category):
        raise Exception("Item already owned.")
        
    player_data["inventory"].add_item(item, category)
    player_data["coins"] -= price
    
    save_game(save_name, player_data)


@error_wrapper
def sell_item(save_name: str, item: str, category: str, price: int):
    player_data = load_game(save_name)
    
    if not player_data["inventory"].contains(item, category):
        raise Exception("Item not owned.")
    
    player_data["inventory"].remove_item(item, category)
    player_data["coins"] += price
    
    save_game(save_name, player_data)


@error_wrapper
def end_game(save_name: str):
    content = load_game(save_name)
    
    content["inventory"] = content["story"]["inventory"]
    content["coins"] = content["story"]["coins"]
    if "new_backstory" in content["story"]:
        content["background"]["backstory"] = content["story"]["new_backstory"]
    if content["story"]["health"] == 0:
        content["death"] = True
    if content["story"]["goal"] != "":
        if content["story"]["goal_status"] == "win":
            content["coins"] += content["story"]["gold_reward"]
            content = update_xp(content, content["story"]["xp_reward"])
            
    content["story"] = {}
    save_game(save_name, content)
    