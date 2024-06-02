import hashlib


def hash_key(key: str) -> str:
    """
    This function is used to hash a key.

    :param key: The key to be hashed.
    :return: The hashed key.
    """
    return hashlib.sha256(key.encode()).hexdigest()


class Connection:
    """
    This is the abstract class for the connection classes.
    The connection classes are used to connect to the database and perform operations on it.
    """

    def read(self, username: str, save_name: str) -> dict | None:
        """
        This method is used to read a specific save's data from the database.
        returns None if the save does not exist.

        :param username: The username of the user.
        :param save_name: The name of the save.
        :return: The data from the database.
        """
        raise NotImplementedError

    def read_all(self, username: str) -> dict:
        """
        This method is used to read all the user's saves from the database.
        Returns an empty dictionary if the data does not exist.

        :param username: The username of the user.
        :return: The data from the database.
        """
        raise NotImplementedError

    def commit(self, username: str, save_name: str, data: dict, timestamp: int) -> None:
        """
        This method is used to commit a save to the database.

        :param username: The username of the user.
        :param save_name: The name of the save.
        :param data: The data to be saved.
        :param timestamp: The timestamp of the save.
        """
        raise NotImplementedError

    def commit_all(self, username: str, data: dict, timestamp: int) -> None:
        """
        This method is used to commit all the user's saves to the database.

        :param username: The username of the user.
        :param data: The data to be saved.
        :param timestamp: The timestamp of the save.
        """
        raise NotImplementedError

    def delete(self, username: str, save_name: str) -> None:
        """
        This method is used to delete a save from the database.

        :param username: The username of the user.
        :param save_name: The name of the save.
        """
        raise NotImplementedError

    def get_all_saves(self, username: str) -> list[str]:
        """
        This method is used to get all the saves of the user.

        :param username: The username of the user.
        :return: The list of save names.
        """
        raise NotImplementedError

    def save_image(self, username: str, save_name: str, image_bytes: bytes) -> None:
        """
        This method is used to save an image to the database.

        :param username: The username of the user.
        :param save_name: The name of the save.
        :param image_bytes: The image bytes.
        """
        raise NotImplementedError

    def return_image_string(self, username: str, save_name: str) -> str:
        """
        This method is used to return the save's image bytes as a string.

        :param username: The username of the user.
        :param save_name: The name of the save.
        :return: The image bytes as a string.
        """
        raise NotImplementedError

    def cache(self, username: str, save_name: str, key: str, data: any) -> None:
        """
        This method is used to cache data in the database.

        :param username: The username of the user.
        :param save_name: The name of the save.
        :param key: The key of the data.
        :param data: The data to be cached.
        """
        raise NotImplementedError

    def get_cache(self, username: str, save_name: str, key: str) -> dict | None:
        """
        This method is used to get cached data from the database.
        Returns None if the data does not exist.

        :param username: The username of the user.
        :param save_name: The name of the save.
        :param key: The key of the data.
        :return: The cached data.
        """
        raise NotImplementedError

    def delete_cache(self, username: str, save_name: str, key: str) -> None:
        """
        This method is used to delete cached data from the database.

        :param username: The username of the user.
        :param save_name: The name of the save.
        :param key: The key of the data.
        """
        raise NotImplementedError

    def delete_all_cache(self, username: str, save_name: str) -> None:
        """
        This method is used to delete all save's cached data from the database.

        :param username: The username of the user.
        :param save_name: The name of the save.
        """
        raise NotImplementedError
