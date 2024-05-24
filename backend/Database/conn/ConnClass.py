class Connection:
    def read(self, username: str, save_name: str):
        raise NotImplementedError

    def commit(self, username: str, save_name: str, data: dict):
        raise NotImplementedError

    def delete(self, username: str, save_name: str):
        raise NotImplementedError

    def get_all_saves(self, username: str) -> list[str]:
        raise NotImplementedError

    def save_image(self, username: str, save_name: str, image_bytes: bytes) -> None:
        raise NotImplementedError

    def return_image_string(self, username: str, save_name: str) -> str:
        raise NotImplementedError
