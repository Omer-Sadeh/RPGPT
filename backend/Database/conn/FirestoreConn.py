import base64
import pathlib

from firebase_admin import credentials, firestore, initialize_app, storage
from backend.Database.conn.ConnClass import Connection, hash_key


class FirestoreConn(Connection):
    """
    This class is used to connect to the Firestore database.
    Can be used only when a Firebase project is set up and FirebaseAuth.json is present in the conn folder.
    """

    def __init__(self):
        cred = credentials.Certificate('backend/Database/conn/FirebaseAuth.json')
        initialize_app(cred, {'storageBucket': 'gengamedatabase.appspot.com'})
        self.db = firestore.client()
        self.bucket = storage.bucket()

    def read(self, username: str, save_name: str) -> dict | None:
        if not username:
            raise Exception("Username not provided.")

        full_data = self.db.collection("users").document(username).get()
        if full_data.exists:
            full_data = full_data.to_dict()
            if save_name not in full_data:
                raise Exception("Save not found!")
            return full_data[save_name]
        else:
            raise Exception("User not found!")

    def read_all(self, username: str) -> dict:
        if not username:
            return {}

        full_data = self.db.collection("users").document(username).get()
        if full_data.exists:
            return full_data.to_dict()
        else:
            return {}

    def commit(self, username: str, save_name: str, data: dict, timestamp: int) -> None:
        if not username:
            return

        full_data = self.db.collection("users").document(username).get()
        if full_data.exists:
            full_data = full_data.to_dict()
            full_data[save_name] = data
        else:
            full_data = {save_name: data}
        full_data["timestamp"] = timestamp

        self.db.collection("users").document(username).set(full_data)

    def commit_all(self, username: str, data: dict, timestamp: int) -> None:
        if not username:
            return

        data["timestamp"] = timestamp
        self.db.collection("users").document(username).set(data)

    def delete(self, username: str, save_name: str) -> None:
        full_data = self.db.collection("users").document(username).get()
        if full_data.exists:
            if save_name in full_data.to_dict():
                self.db.collection("users").document(username).update({save_name: firestore.DELETE_FIELD})

        cache_data = self.db.collection("cache").document(username).get()
        if cache_data.exists:
            if save_name in cache_data.to_dict():
                self.db.collection("cache").document(username).update({save_name: firestore.DELETE_FIELD})

        img_categories = ["shop", "character", "scene"]
        for category in img_categories:
            blob = self.bucket.blob(username + "_" + save_name + "_" + category + ".png")
            if blob.exists():
                blob.delete()

    def get_all_saves(self, username: str) -> list[str]:
        if not username:
            return []

        full_data = self.db.collection("users").document(username).get()
        if full_data.exists:
            full_data = full_data.to_dict()
            key_list = list(full_data.keys())
            if "timestamp" in key_list:
                key_list.remove("timestamp")
            return key_list
        else:
            return []

    def save_image(self, username: str, save_name: str, category: str, image_bytes: bytes) -> None:
        blob = self.bucket.blob(username + "_" + save_name + "_" + category + ".png")
        blob.upload_from_string(image_bytes, content_type='image/png')

    def return_image_string(self, username: str, save_name: str, category: str) -> str:
        blob = self.bucket.blob(username + "_" + save_name + "_" + category + ".png")
        if not blob.exists():
            with open(str(pathlib.Path(__file__).parent.resolve()) + "/default_" + category + ".png", "rb") as image_file:
                return base64.b64encode(image_file.read()).decode()
        img_bytes = blob.download_as_string()
        return base64.b64encode(img_bytes).decode()

    def cache(self, username: str, save_name: str, key: str, data: any) -> None:
        if not self.db.collection("cache").document(username).get().exists:
            self.db.collection("cache").document(username).set({}, merge=True)
        self.db.collection("cache").document(username).update({f"{save_name}.{hash_key(key)}": data})

    def get_cache(self, username: str, save_name: str, key: str) -> dict | None:
        cache_data = self.db.collection("cache").document(username).get()
        if cache_data.exists:
            cache_data = cache_data.to_dict()
            if save_name in cache_data and hash_key(key) in cache_data[save_name]:
                return cache_data[save_name][hash_key(key)]
        return None

    def delete_cache(self, username: str, save_name: str, key: str) -> None:
        if self.db.collection("cache").document(username).get().exists:
            self.db.collection("cache").document(username).update({f"{save_name}.{hash_key(key)}": firestore.DELETE_FIELD})

    def delete_all_cache(self, username: str, save_name: str) -> None:
        if self.db.collection("cache").document(username).get().exists:
            self.db.collection("cache").document(username).update({save_name: firestore.DELETE_FIELD})
