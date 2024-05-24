import logging
from backend.SNS.I_Check import Check, EditCheck


class LengthCheck(Check):
    block_msg = "Too many words."

    def __init__(self, max_length: int):
        self.max_length = max_length

    def run(self, req: str) -> bool:
        """
        Check the length of the request.

        :param req: The request to check.
        :return: True if the request is within the max length, False otherwise.
        """
        num_words = len(req.split())
        if num_words > self.max_length or num_words < 1:
            logging.error(f"Invalid request, too many words: {num_words}")
            return False
        return True


class InvalidCharsCheck(Check):
    block_msg = "Invalid character."

    def __init__(self, invalid_chars: list):
        self.invalid_chars = invalid_chars

    def run(self, req: str) -> bool:
        """
        Check for invalid characters in the request.

        :param req: The request to check.
        :return: True if the request does not contain invalid characters, False otherwise.
        """
        for char in self.invalid_chars:
            if char in req:
                logging.error(f"Invalid request, invalid character: {char}")
                return False
        return True


class InvalidExpressionsCheck(Check):
    block_msg = "Invalid expression."

    def __init__(self, invalid_expressions: list):
        self.invalid_expressions = invalid_expressions

    def run(self, req: str) -> bool:
        """
        Check for invalid expressions in the request.

        :param req: The request to check.
        :return: True if the request does not contain invalid expressions, False otherwise.
        """
        for expr in self.invalid_expressions:
            if expr in req.lower():
                logging.error(f"Invalid request, invalid expression: {expr}")
                return False
        return True


class SpecialCharsCheck(EditCheck):
    block_msg = "Special character masked."
    additional_chars_to_mask = []
    mask = '_'

    def __init__(self, additional_chars_to_mask=None, mask='_'):
        if additional_chars_to_mask is not None:
            self.additional_chars_to_mask = additional_chars_to_mask
        self.mask = mask

    def run(self, req: str) -> str:
        """
        Mask special characters in the request.
        That is, characters that are not letters or numbers.

        :param req: The request to check.
        :return: The request with special characters replaced by a mask.
        """
        logging.info(f"Masking special characters in request: {req}")
        new_req = req
        for char in req:
            if (not char.isalnum() and char is not ' ') or char in self.additional_chars_to_mask:
                logging.warning(f"Masking special character: {char}")
                new_req = new_req.replace(char, self.mask)
                logging.debug(f"Masked request: {new_req}")
        new_req = req.replace(' ', '_')
        logging.debug(f"Final masked request: {new_req}")
        return new_req
