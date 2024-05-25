import logging
from backend.Types.SaveData import SaveData
from backend.Database.conn.ConnClass import Connection
from backend.Database.conn.FirestoreConn import FirestoreConn
from backend.Database.conn.LocalConn import LocalConn


class DataBase:
    conn: Connection = None
    gen_img: bool = False

    def __init__(self):
        try:
            self.conn = FirestoreConn()
        except Exception as e:
            logging.warning(f"Failed to connect to Firestore: {e}. Using local Database.")
            self.conn = LocalConn()

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
            return

        self.conn.commit(username, save_name, data.to_dict())
        logging.info(f"Save completed: {save_name}")

    def create_save(self, username: str, save_name: str, data: SaveData) -> None:
        """
        Creates a new save file with the given name and data.

        :param save_name: the name of the save file
        :param data: the data to be saved
        """
        if self.save_exists(username, save_name):
            raise Exception("Save already exists.")

        logging.info(f"Creating save: {save_name}")
        self.conn.commit(username, save_name, data.to_dict())
        logging.info(f"Save created: {save_name}")

    def delete_save(self, username: str, save_name: str) -> None:
        """
        Deletes the save file with the given name.

        :param save_name: the name of the save file
        """
        logging.info(f"Deleting save: {save_name}")
        self.conn.delete(username, save_name)
        logging.info(f"Save deleted: {save_name}")

    def saves_list(self, username: str) -> list[str]:
        """
        Returns the list of user's saves in the Database.
        """
        return self.conn.get_all_saves(username)

    def save_exists(self, username: str, save_name: str):
        return save_name in self.saves_list(username)

    def save_image(self, username: str, save_name: str, image_bytes: bytes) -> None:
        """
        Saves the image to the save file with the given name.

        :param save_name: the name of the save file
        :param image_bytes: the image to be saved
        """
        self.conn.save_image(username, save_name, image_bytes)
        logging.info(f"Image saved: {save_name}")

    def get_save_image(self, username: str, save_name: str) -> str:
        """
        Returns the image of the save file with the given name.

        :return: the image of the save file, as a base64 encoded string
        """
        return self.conn.return_image_string(username, save_name)
