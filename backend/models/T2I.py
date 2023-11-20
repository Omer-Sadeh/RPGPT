import io
import json
import os
from PIL import Image
import requests
from backend.Utility import *

IMAGE_API_URL = "https://api-inference.huggingface.co/models/prompthero/openjourney-v4"


# ---------------- Utilities ---------------- #


def is_valid_image(image_bytes):
    try:
        Image.open(io.BytesIO(image_bytes)).verify()
        return True
    except Exception as _:
        return False
    
    
# ---------------- API ---------------- #


@error_wrapper
def generate(prompt, save_location):
    id = os.getenv('HUGGINGFACE_BEARER')
    headers = {"Authorization": id}
    if id is None:
        raise Exception("HuggingFace Bearer token not found")

    image_bytes = requests.post(IMAGE_API_URL, headers=headers, json={"inputs": prompt}).content
    valid = is_valid_image(image_bytes)
    if valid:
        image = Image.open(io.BytesIO(image_bytes))
        image.save(save_location)
        return image_bytes
    else:
        image_bytes = json.loads(image_bytes)
        if 'error' in image_bytes:
            raise Exception(image_bytes['error'])
        raise Exception("Invalid image: " + str(image_bytes))
