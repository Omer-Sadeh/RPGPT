import logging
import time
from backend.Types.SaveData import SaveData
from backend.Database.conn.ConnClass import Connection
from backend.Database.conn.FirestoreConn import FirestoreConn
from backend.Utility import start_promise, CustomException


def get_current_timestamp() -> int:
    """
    Returns the current timestamp in minutes.

    :return: the current timestamp
    """
    return int(time.time())


class DataBase:
    conn: Connection = None
    gen_img: bool = False

    def __init__(self):
        try:
            self.conn = FirestoreConn()
        except Exception as e:
            raise CustomException(f"Failed to connect to database: {e}.")

    def get_save_data(self, username: str, save_name: str) -> SaveData:
        """
        Returns the content of the save file.

        :return: the content of the save file
        """
        return SaveData(self.conn.read(username, save_name))

    def save_game_data(self, username: str, save_name: str, data: SaveData) -> None:
        """
        Saves the current game data to the Database.
        """
        logging.info(f"Saving game: {save_name}")
        logging.debug(f"Data: {data}")
        if data.ver < self.get_save_data(username, save_name).ver:
            logging.warning("Tried to commit earlier version. aborting commit.")
        else:
            timestamp = get_current_timestamp()
            self.conn.commit(username, save_name, data.to_dict(), timestamp)
        logging.info(f"Save completed: {save_name}")

    def create_save(self, username: str, save_name: str, data: SaveData) -> None:
        """
        Creates a new save file with the given name and data.

        :param username: the name of the user
        :param save_name: the name of the save file
        :param data: the data to be saved
        """
        if self.save_exists(username, save_name):
            raise Exception("Save already exists.")

        logging.info(f"Creating save: {save_name}")
        timestamp = get_current_timestamp()
        self.conn.commit(username, save_name, data.to_dict(), timestamp)
        logging.info(f"Save created: {save_name}")

    def delete_save(self, username: str, save_name: str) -> None:
        """
        Deletes the save file with the given name.

        :param username: the name of the user
        :param save_name: the name of the save file
        """
        logging.info(f"Deleting save: {save_name}")
        self.conn.delete(username, save_name)
        logging.info(f"Save deleted: {save_name}")

    def saves_list(self, username: str) -> dict:
        """
        Returns the list of user's saves in the Database.
        """
        ids = self.conn.get_all_saves(username)
        saves_list = {}
        for save_id in ids:
            saves_list[save_id] = self.get_save_data(username, save_id).background["name"]
        return saves_list

    def save_exists(self, username: str, save_name: str):
        return save_name in self.saves_list(username)

    def save_image(self, username: str, save_name: str, category: str, image_bytes: bytes) -> None:
        """
        Saves the image to the save file with the given name.

        :param username: the name of the user
        :param save_name: the name of the save file
        :param category: the category of the image
        :param image_bytes: the image to be saved
        """
        self.conn.save_image(username, save_name, category, image_bytes)
        logging.info(f"Image saved: {save_name}")

    def get_save_image(self, username: str, save_name: str, category: str) -> str:
        """
        Returns the image of the save file with the given name.

        :param username: the name of the user
        :param save_name: the name of the save file
        :param category: the category of the image
        :return: the image of the save file, as a base64 encoded string
        """
        return self.conn.return_image_string(username, save_name, category)

    def cache(self, username: str, save_name: str, key: str, data: any):
        """
        Adds a cache to the save file with the given name.

        :param username: the name of the user
        :param save_name: the name of the save file
        :param key: the key of the cache
        :param data: the data to be cached
        """
        self.conn.cache(username, save_name, key, data)

    def get_cache(self, username: str, save_name: str, key: str):
        """
        Returns the cache of the save file with the given name.

        :param username: the name of the user
        :param save_name: the name of the save file
        :param key: the key of the cache
        :return: the cache of the save file
        """
        return self.conn.get_cache(username, save_name, key)

    def delete_cache(self, username: str, save_name: str, key: str):
        """
        Deletes the cache of the save file with the given name.

        :param username: the name of the user
        :param save_name: the name of the save file
        :param key: the key of the cache
        """
        self.conn.delete_cache(username, save_name, key)

    def delete_all_cache(self, username: str, save_name: str):
        """
        Deletes all caches of the save file with the given name.

        :param username: the name of the user
        :param save_name: the name of the save file
        """
        self.conn.delete_all_cache(username, save_name)
