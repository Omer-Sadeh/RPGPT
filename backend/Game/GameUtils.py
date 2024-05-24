import logging
import random
from backend.SNS import SNS
from backend.Types.SaveData import SaveData


def probability_function(probability: float) -> str:
    """
    runs a probability function, and returns "Success" or "Failure" based on the random number generated

    :param probability: float between 0 and 1
    :return: "Success" or "Failure"
    """
    if 0 <= probability <= 1:
        random_number = random.random()
        logging.debug(f"Required probability: {probability}, Random number: {random_number}")
        if random_number < probability:
            logging.info("Probability result: Success!")
            return "Success"
        else:
            logging.info("Probability result: Failure!")
            return "Failure"
    else:
        logging.error("Probability out of bounds!")
        raise ValueError('Probability must be between 0 and 1.')


def calculate_success_rate(data: SaveData, index: int) -> float:
    """
    Calculates the success rate of an option based on the story's data.

    :param data: the story's data
    :param index: the index of the option in the story
    :return: the updated success rate
    """
    logging.info(f"Calculating success rate for option {index}...")
    base_rate = data.story["rates"][index]
    logging.debug(f"Base rate: {base_rate}")
    updated_rate = base_rate
    skills = list(data.skills.keys())

    if len(data.story["history"]) > 0:
        advantage_skill = data.story["advantages"][index]
        logging.debug(f"Advantage skill: {advantage_skill}")
        if advantage_skill not in skills:
            logging.debug(f"Advantage skill not found, using {skills[0]} instead.")
            advantage_skill = skills[0]
        advantage_level = data.story["levels"][index]
        logging.debug(f"Advantage level: {advantage_level}")
        if data.skills[advantage_skill] >= advantage_level:
            logging.debug(f"Advantage skill level is higher than required: {data.skills[advantage_skill]}")
            updated_rate += (1 - base_rate) * 0.75
        else:
            logging.debug(f"Advantage skill level is lower than required: {data.skills[advantage_skill]}")

    logging.info(f"Final rate: {updated_rate}")
    return updated_rate


def process_save_name(save_name: str):
    """
    Processes the save name using the SNS service.

    :param save_name: the save name to process
    :return: the updated save name
    """
    sns_result = SNS.save_system(save_name)
    if not sns_result:
        raise Exception("Save name is invalid. save name: " + save_name + ", reason: " + sns_result.reason)
    logging.debug(f"SNS save result: {sns_result}")
    return sns_result.updated_req

