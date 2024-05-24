import ast
from backend.Utility import *


class Model:
    num_of_retries = 2
    history_window_size = 20

    def sys_footer(self) -> str:
        raise NotImplementedError

    def _request(self, system_message: str, request: str) -> str:
        """
        Request a response from the model

        :param system_message: The system message
        :param request: The user request
        :return: The response from the model
        """
        raise NotImplementedError

    @error_wrapper
    def generate(self, system: str, request: str) -> str:
        """
        Generate a response from the model

        :param system: The system message
        :param request: The user request
        :return: The response from the model
        """
        retries = self.num_of_retries
        while retries > 0:
            try:
                return self._request(request, system)
            except Exception as exc:
                retries -= 1
                if retries == 0:
                    raise exc

    @error_wrapper
    def generate_json(self, system: str, request: str) -> dict:
        """
        Generate a response from the model and parse it as JSON

        :param system: The system message
        :param request: The user request
        :return: The response from the model as JSON
        """
        result = self.generate(request, system)
        if result["status"] == "success":
            try:
                response = result["result"]
                if response.startswith("```"):
                    response = response[response.find("\n"):]
                    response = response[:response.rfind("\n")]
                return ast.literal_eval(response)
            except Exception as _:
                raise Exception("Error parsing JSON.\n" + result["result"])
        else:
            raise Exception(result["reason"])
