import base64
from firebase_admin import credentials, firestore, initialize_app, storage
from backend.Database.conn.ConnClass import Connection


class FirestoreConn(Connection):
    def __init__(self):
        cred = credentials.Certificate('backend/Database/conn/FirebaseAuth.json')
        initialize_app(cred, {'storageBucket': 'gengamedatabase.appspot.com'})
        self.db = firestore.client()
        self.bucket = storage.bucket()

    def read(self, username: str, save_name: str):
        if not username:
            return None

        full_data = self.db.collection("users").document(username).get()
        if full_data.exists:
            full_data = full_data.to_dict()
            return full_data[save_name]
        else:
            return None

    def commit(self, username: str, save_name: str, data: dict):
        if not username:
            return

        full_data = self.db.collection("users").document(username).get()
        if full_data.exists:
            full_data = full_data.to_dict()
            full_data[save_name] = data
        else:
            full_data = {save_name: data}

        self.db.collection("users").document(username).set(full_data)

    def delete(self, username: str, save_name: str):
        full_data = self.db.collection("users").document(username).get()
        if full_data.exists:
            if save_name in full_data.to_dict():
                self.db.collection("users").document(username).update({save_name: firestore.DELETE_FIELD})

    def get_all_saves(self, username: str) -> list[str]:
        if not username:
            return []

        full_data = self.db.collection("users").document(username).get()
        if full_data.exists:
            full_data = full_data.to_dict()
            return list(full_data.keys())
        else:
            return []

    def save_image(self, username: str, save_name: str, image_bytes: bytes) -> None:
        blob = self.bucket.blob(username + "_" + save_name + ".png")
        blob.upload_from_string(image_bytes, content_type='image/png')

    def return_image_string(self, username: str, save_name: str) -> str:
        blob = self.bucket.blob(username + "_" + save_name + ".png")
        if not blob.exists():
            raise Exception("Image does not exist.")
        img_bytes = blob.download_as_string()
        return base64.b64encode(img_bytes).decode()
