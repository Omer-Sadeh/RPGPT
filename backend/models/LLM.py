import os
import openai
from backend.Utility import *


# ---------------- Utilities ---------------- #


def model_request(messages):
    result = openai.ChatCompletion.create(model="gpt-4", messages=messages)
    for choice in result.choices:
        if "text" in choice:
            return choice.text
    return result['choices'][0]['message']['content']


# ---------------- API ---------------- #
    

@error_wrapper
def generate(messages):
    key = os.getenv('OPENAI_KEY')
    openai.api_key = key
    if key is None:
        raise Exception("OpenAI key not found")
    
    retries = 3
    while retries > 0:
        try:
            return model_request(messages)
        except Exception as exc:
            retries -= 1
            if retries == 0:
                raise exc
