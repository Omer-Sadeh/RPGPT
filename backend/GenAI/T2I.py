import io
import json
import os
from PIL import Image
import requests
from backend.Utility import *

# The URL for the image API
IMAGE_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"


# ---------------- Utilities ---------------- #


def is_valid_image(image_bytes):
    """
    Check if the image bytes are valid

    :param image_bytes: The image bytes
    :return: True if the image bytes are valid, False otherwise
    """
    try:
        Image.open(io.BytesIO(image_bytes)).verify()
        return True
    except Exception as _:
        return False
    
    
# ---------------- API ---------------- #


@error_wrapper
def generate(prompt) -> bytes:
    """
    Generate an image from the prompt

    :param prompt: The prompt to generate the image from
    :return: The generated image bytes
    """
    logging.info(f"Generating image for prompt: {prompt}")
    id = os.getenv('HUGGINGFACE_BEARER')
    headers = {"Authorization": id}
    if id is None:
        logging.error("HuggingFace Bearer token not found!")
        raise Exception("HuggingFace Bearer token not found")

    image_bytes = requests.post(IMAGE_API_URL, headers=headers, json={"inputs": prompt}).content
    valid = is_valid_image(image_bytes)
    if valid:
        logging.debug(f"Image generated successfully for prompt: {prompt}")
        return image_bytes
    else:
        image_bytes = json.loads(image_bytes)
        if 'error' in image_bytes:
            logging.error(image_bytes['error'])
            raise Exception(image_bytes['error'])
        raise Exception("Invalid image: " + str(image_bytes))
