class Check:
    block_msg: str

    def run(self, req: str) -> bool:
        raise NotImplementedError


class EditCheck(Check):
    def run(self, req: str) -> str:
        raise NotImplementedError
