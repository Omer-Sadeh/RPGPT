import base64
import io
import json
import logging
import os
import pathlib
import threading
from PIL import Image
from backend.Database.conn.ConnClass import Connection, hash_key


class LocalConn(Connection):
    """
    This class is used to connect to the local database.
    The local database is a folder in the backend directory that contains the user's data.
    """

    saves_path = str(pathlib.Path(__file__).parent.resolve()) + '/local_db'
    save_lock = threading.Lock()
    cache_lock = threading.Lock()

    def __init__(self):
        if not os.path.exists(self.saves_path):
            os.mkdir(self.saves_path)

    @staticmethod
    def save_lock_wrapper(func):
        def wrapper(self, *args, **kwargs):
            self.save_lock.acquire()
            logging.info(f"save-Lock acquired by {func.__name__}")
            result = func(self, *args, **kwargs)
            logging.info(f"save-Lock released by {func.__name__}")
            self.save_lock.release()
            return result
        return wrapper

    @staticmethod
    def cache_lock_wrapper(func):
        def wrapper(self, *args, **kwargs):
            self.cache_lock.acquire()
            logging.info(f"cache-Lock acquired by {func.__name__}")
            result = func(self, *args, **kwargs)
            logging.info(f"cache-Lock released by {func.__name__}")
            self.cache_lock.release()
            return result
        return wrapper

    def get_save_path(self, username: str) -> str:
        return self.saves_path + "/" + str(username) + ".json"

    def get_cache_path(self, username: str) -> str:
        return self.saves_path + "/" + str(username) + "_cache.json"

    def get_image_path(self, username: str, save_name: str, category: str) -> str:
        return self.saves_path + "/" + str(username) + "_" + save_name + "_" + category + ".png"

    def validate_user_file(self, username: str) -> None:
        """
        This method is used to validate the user files, creating them if they do not exist.
        """
        if not os.path.exists(self.get_save_path(username)):
            with open(self.get_save_path(username), "w") as save_file:
                json.dump({}, save_file, indent=2, separators=(', ', ' : '))

        if not os.path.exists(self.get_cache_path(username)):
            with open(self.get_cache_path(username), "w") as save_file:
                json.dump({}, save_file, indent=2, separators=(', ', ' : '))

    def read(self, username: str, save_name: str) -> dict | None:
        self.validate_user_file(username)
        with open(self.get_save_path(username), "r") as save_file:
            data = json.load(save_file)
        if save_name not in data:
            return None
        return data[save_name]

    def read_all(self, username: str) -> dict:
        self.validate_user_file(username)
        with open(self.get_save_path(username), "r") as save_file:
            return json.load(save_file)

    @save_lock_wrapper
    def commit(self, username: str, save_name: str, data: dict, timestamp: int) -> None:
        self.validate_user_file(username)
        with open(self.get_save_path(username), "r") as save_file:
            user_data = json.load(save_file)
        with open(self.get_save_path(username), "w") as save_file:
            user_data[save_name] = data
            user_data["timestamp"] = timestamp
            json.dump(user_data, save_file, indent=2, separators=(', ', ' : '))

    @save_lock_wrapper
    def commit_all(self, username: str, data: dict, timestamp: int) -> None:
        self.validate_user_file(username)
        with open(self.get_save_path(username), "w") as save_file:
            data["timestamp"] = timestamp
            json.dump(data, save_file, indent=2, separators=(', ', ' : '))

    @save_lock_wrapper
    def delete(self, username: str, save_name: str) -> None:
        self.validate_user_file(username)
        with open(self.get_save_path(username), "r") as save_file:
            user_data = json.load(save_file)
        with open(self.get_save_path(username), "w") as save_file:
            del user_data[save_name]
            json.dump(user_data, save_file, indent=2, separators=(', ', ' : '))

        img_categories = ["shop", "character", "scene"]
        for category in img_categories:
            if os.path.exists(self.get_image_path(username, save_name, category)):
                os.remove(self.get_image_path(username, save_name, category))

    def get_all_saves(self, username: str) -> list[str]:
        self.validate_user_file(username)
        with open(self.get_save_path(username), "r") as save_file:
            user_data = json.load(save_file)

        key_list = list(user_data.keys())
        if "timestamp" in key_list:
            key_list.remove("timestamp")
        return key_list

    def save_image(self, username: str, save_name: str, category: str, image_bytes: bytes) -> None:
        image = Image.open(io.BytesIO(image_bytes))
        image.save(self.get_image_path(username, save_name, category))

    def return_image_string(self, username: str, save_name: str, category: str) -> str:
        if not os.path.exists(self.get_image_path(username, save_name, category)):
            with open(str(pathlib.Path(__file__).parent.resolve()) + "/default_" + category + ".png", "rb") as image_file:
                return base64.b64encode(image_file.read()).decode()
        with open(self.get_image_path(username, save_name, category), "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()

    @cache_lock_wrapper
    def cache(self, username: str, save_name: str, key: str, data: any) -> None:
        self.validate_user_file(username)
        try:
            with open(self.get_cache_path(username), "r") as save_file:
                cache_data = json.load(save_file)
        except Exception:
            cache_data = {}
        with open(self.get_cache_path(username), "w") as save_file:
            if save_name not in cache_data:
                cache_data[save_name] = {}
            cache_data[save_name][hash_key(key)] = data
            json.dump(cache_data, save_file, indent=2, separators=(', ', ' : '))

    def get_cache(self, username: str, save_name: str, key: str) -> dict | None:
        self.validate_user_file(username)
        try:
            with open(self.get_cache_path(username), "r") as save_file:
                cache_data = json.load(save_file)
        except Exception:
            cache_data = {}
        if save_name not in cache_data or hash_key(key) not in cache_data[save_name]:
            return None
        return cache_data[save_name][hash_key(key)]

    @cache_lock_wrapper
    def delete_cache(self, username: str, save_name: str, key: str) -> None:
        self.validate_user_file(username)
        try:
            with open(self.get_cache_path(username), "r") as save_file:
                cache_data = json.load(save_file)
        except Exception:
            cache_data = {}
        with open(self.get_cache_path(username), "w") as save_file:
            del cache_data[save_name][hash_key(key)]
            json.dump(cache_data, save_file, indent=2, separators=(', ', ' : '))

    @cache_lock_wrapper
    def delete_all_cache(self, username: str, save_name: str) -> None:
        self.validate_user_file(username)
        try:
            with open(self.get_cache_path(username), "r") as save_file:
                cache_data = json.load(save_file)
        except Exception:
            cache_data = {}
        with open(self.get_cache_path(username), "w") as save_file:
            if save_name in cache_data:
                del cache_data[save_name]
            json.dump(cache_data, save_file, indent=2, separators=(', ', ' : '))
