import base64
import io
import json
import os
import pathlib
from PIL import Image
from backend.Database.conn.ConnClass import Connection


class LocalConn(Connection):
    saves_path = str(pathlib.Path(__file__).parent.resolve()) + '/local_db'

    def __init__(self):
        if not os.path.exists(self.saves_path):
            os.mkdir(self.saves_path)

    def get_save_path(self, username: str):
        return self.saves_path + "/" + str(username) + ".json"

    def get_image_path(self, username: str, save_name: str):
        return self.saves_path + "/" + str(username) + "_" + save_name + ".png"

    def validate_user_file(self, username: str):
        if not os.path.exists(self.get_save_path(username)):
            with open(self.get_save_path(username), "w") as save_file:
                json.dump({}, save_file, indent=2, separators=(', ', ' : '))

    def read(self, username: str, save_name: str):
        self.validate_user_file(username)
        with open(self.get_save_path(username), "r") as save_file:
            data = json.load(save_file)
        return data[save_name]

    def commit(self, username: str, save_name: str, data: dict):
        self.validate_user_file(username)
        with open(self.get_save_path(username), "r") as save_file:
            user_data = json.load(save_file)
        with open(self.get_save_path(username), "w") as save_file:
            user_data[save_name] = data
            json.dump(user_data, save_file, indent=2, separators=(', ', ' : '))

    def delete(self, username: str, save_name: str):
        self.validate_user_file(username)
        with open(self.get_save_path(username), "r") as save_file:
            user_data = json.load(save_file)
        with open(self.get_save_path(username), "w") as save_file:
            del user_data[save_name]
            json.dump(user_data, save_file, indent=2, separators=(', ', ' : '))
        if os.path.exists(self.get_image_path(username, save_name)):
            os.remove(self.get_image_path(username, save_name))

    def get_all_saves(self, username: str) -> list[str]:
        self.validate_user_file(username)
        with open(self.get_save_path(username), "r") as save_file:
            user_data = json.load(save_file)
        return list(user_data.keys())

    def save_image(self, username: str, save_name: str, image_bytes: bytes) -> None:
        image = Image.open(io.BytesIO(image_bytes))
        image.save(self.get_image_path(username, save_name))

    def return_image_string(self, username: str, save_name: str) -> str:
        if not os.path.exists(self.get_image_path(username, save_name)):
            raise Exception("No image found.")
        with open(self.get_image_path(username, save_name), "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
