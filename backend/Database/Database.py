import logging
import time
from backend.Types.SaveData import SaveData
from backend.Database.conn.ConnClass import Connection
from backend.Database.conn.FirestoreConn import FirestoreConn
from backend.Database.conn.LocalConn import LocalConn
from backend.Utility import start_promise


def get_current_timestamp() -> int:
    """
    Returns the current timestamp in minutes.

    :return: the current timestamp
    """
    return int(time.time())


class DataBase:
    local_conn: Connection = None
    cloud_conn: Connection = None
    gen_img: bool = False

    def __init__(self):
        self.local_conn = LocalConn()
        try:
            self.cloud_conn = FirestoreConn()
        except Exception as e:
            logging.warning(f"Failed to connect to Firestore: {e}. No cloud used.")

    def sync_conns(self, username: str) -> None:
        """
        Syncs the local and cloud databases, choosing the conn with the newer timestamp.

        :param username: the name of the user
        """
        if self.cloud_conn is not None:
            if self.cloud_conn is not None:
                cloud_data = self.cloud_conn.read_all(username)
                local_data = self.local_conn.read_all(username)

                if cloud_data is None and local_data is None:
                    return
                if cloud_data is None:
                    self.cloud_conn.commit_all(username, local_data, get_current_timestamp())
                    return
                if local_data is None:
                    self.local_conn.commit_all(username, cloud_data, get_current_timestamp())
                    return

                cloud_time = cloud_data.get("timestamp", 0)
                local_time = local_data.get("timestamp", 0)
                if cloud_time > local_time:
                    self.local_conn.commit_all(username, cloud_data, cloud_time)
                elif cloud_time < local_time:
                    self.cloud_conn.commit_all(username, local_data, local_time)

    def get_save_data(self, username: str, save_name: str) -> SaveData:
        """
        Returns the content of the save file.

        :return: the content of the save file
        """
        try:
            return SaveData(self.local_conn.read(username, save_name))
        except Exception as e:
            logging.warning(f"Failed to read local save: {e}")
            if self.cloud_conn is not None:
                full_data = self.cloud_conn.read_all(username)
                if save_name not in full_data:
                    raise Exception("Save not found")
                data = SaveData(full_data[save_name])
                self.local_conn.commit_all(username, full_data, get_current_timestamp())
                return data
            else:
                raise e

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
            self.local_conn.commit(username, save_name, data.to_dict(), timestamp)
            if self.cloud_conn is not None:
                start_promise(self.cloud_conn.commit, username, save_name, data.to_dict(), timestamp)
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
        self.local_conn.commit(username, save_name, data.to_dict(), timestamp)
        if self.cloud_conn is not None:
            start_promise(self.cloud_conn.commit, username, save_name, data.to_dict(), timestamp)
        logging.info(f"Save created: {save_name}")

    def delete_save(self, username: str, save_name: str) -> None:
        """
        Deletes the save file with the given name.

        :param username: the name of the user
        :param save_name: the name of the save file
        """
        logging.info(f"Deleting save: {save_name}")
        self.local_conn.delete(username, save_name)
        if self.cloud_conn is not None:
            start_promise(self.cloud_conn.delete, username, save_name)
        logging.info(f"Save deleted: {save_name}")

    def saves_list(self, username: str) -> list[str]:
        """
        Returns the list of user's saves in the Database.
        """
        try:
            return self.local_conn.get_all_saves(username)
        except Exception as e:
            logging.warning(f"Failed to read local saves: {e}")
            if self.cloud_conn is not None:
                full_data = self.cloud_conn.read_all(username)
                self.local_conn.commit_all(username, full_data, get_current_timestamp())
                return list(full_data.keys())
            else:
                raise e

    def save_exists(self, username: str, save_name: str):
        return save_name in self.saves_list(username)

    def save_image(self, username: str, save_name: str, image_bytes: bytes) -> None:
        """
        Saves the image to the save file with the given name.

        :param username: the name of the user
        :param save_name: the name of the save file
        :param image_bytes: the image to be saved
        """
        self.local_conn.save_image(username, save_name, image_bytes)
        logging.info(f"Image saved: {save_name}")

    def get_save_image(self, username: str, save_name: str) -> str:
        """
        Returns the image of the save file with the given name.

        :return: the image of the save file, as a base64 encoded string
        """
        return self.local_conn.return_image_string(username, save_name)

    def cache(self, username: str, save_name: str, key: str, data: any):
        """
        Adds a cache to the save file with the given name.

        :param username: the name of the user
        :param save_name: the name of the save file
        :param key: the key of the cache
        :param data: the data to be cached
        """
        self.local_conn.cache(username, save_name, key, data)

    def get_cache(self, username: str, save_name: str, key: str):
        """
        Returns the cache of the save file with the given name.

        :param username: the name of the user
        :param save_name: the name of the save file
        :param key: the key of the cache
        :return: the cache of the save file
        """
        return self.local_conn.get_cache(username, save_name, key)

    def delete_cache(self, username: str, save_name: str, key: str):
        """
        Deletes the cache of the save file with the given name.

        :param username: the name of the user
        :param save_name: the name of the save file
        :param key: the key of the cache
        """
        self.local_conn.delete_cache(username, save_name, key)

    def delete_all_cache(self, username: str, save_name: str):
        """
        Deletes all caches of the save file with the given name.

        :param username: the name of the user
        :param save_name: the name of the save file
        """
        self.local_conn.delete_all_cache(username, save_name)
