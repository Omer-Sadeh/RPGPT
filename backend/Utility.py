import concurrent.futures
from backend import DEBUG
import logging

async_context = concurrent.futures.ThreadPoolExecutor()
logging.basicConfig(filename='backend/app.log', filemode='w', level=logging.DEBUG if DEBUG else logging.INFO,
                    format='(%(process)d): %(asctime)s - %(name)s [%(thread)d] - [%(levelname)s] - %(message)s', datefmt='%H:%M:%S')


def build_success_response(result: any) -> dict:
    """
    Builds a success response dictionary with the given result.

    :param result: the result to be included in the response
    :return: the success response dictionary
    """
    return {"status": "success", "result": result}


def build_error_response(reason: str) -> dict:
    """
    Builds an error response dictionary with the given reason.

    :param reason: the reason for the error
    :return: the error response dictionary
    """
    return {"status": "error", "reason": reason}


class CustomException(Exception):
    """ custom exception class for specific error messages """


def error_wrapper(func: callable) -> callable:
    """
    Wraps a function with a try-except block to catch any exceptions that occur during its execution.
    The wrapped function returns a dictionary with the status of the operation and the result of the function,
    in the following format:
    - If the function executes successfully: {"status": "success", "result": <result>}
    - If an exception occurs: {"status": "error", "reason": <reason>}
    If DEBUG is set to True, the dictionary will contain the exception message in the "reason" field.

    :param func: the function to be wrapped
    :return: the wrapped function
    """
    def wrapper(*args, **kwargs):
        try:
            return build_success_response(func(*args, **kwargs))
        except CustomException as exc:
            logging.warning(f"Custom exception found in: {func.__name__}: {str(exc)}")
            return build_error_response(str(exc))
        except Exception as exc:
            logging.exception(f"exception found in: {func.__name__}:")
            return build_error_response("The server encountered an error while processing the request.")
    return wrapper


def APIEndpoint(func: callable) -> callable:
    """
    Wraps a function with the error_wrapper function to catch any exceptions that occur during its execution.
    The wrapped function returns a dictionary with the status of the operation and the result of the function,
    in the following format:
    - If the function executes successfully: {"status": "success", "result": <result>}
    - If an exception occurs: {"status": "error", "reason": <reason>}
    If DEBUG is set to True, the dictionary will contain the exception message in the "reason" field.

    The wrapped function also logs the start and end of the API call,
    as well as the result of the function if it executes successfully.

    :param func: the function to be wrapped
    :return: the wrapped function
    """
    def wrapper(*args, **kwargs):
        logging.info(f"--------- API call: {func.__name__} started!")
        logging.debug(f"Arguments: {args}, {kwargs}")
        result = error_wrapper(func)(*args, **kwargs)
        logging.info(f"--------- API call: {func.__name__} finished!")
        if result["status"] == "success":
            if func.__name__ != "get_image":
                logging.debug(f"--------- {func.__name__} result: {result}")
        return result
    return wrapper


def start_promise(function: callable, *args, **kwargs) -> concurrent.futures.Future:
    """
    Starts a promise with the given function and arguments.
    The promise is submitted to the async context.

    :param function: the function to be executed
    :param args: the arguments to be passed to the function
    :param kwargs: the keyword arguments to be passed to the function
    """
    def handle_exception(promise_obj):
        try:
            promise_obj.result()
        except Exception as e:
            logging.warning(f"An error occurred while executing the promise: {str(promise_obj)}, {str(e)}")
            pass

    promise = async_context.submit(function, *args, **kwargs)
    promise.add_done_callback(handle_exception)
    logging.debug(f"Promise started: {str(function.__name__)}")
    return promise


def await_promise(promise: concurrent.futures.Future) -> dict:
    """
    Waits for the promise to complete and returns the result.

    :param promise: the promise to be awaited
    :return: the result of the promise
    """
    try:
        result = promise.result()
        logging.debug(f"Promise completed, result: {str(result)}")
        return result
    except Exception as e:
        logging.warning(f"An error occurred while awaiting a promise: {str(e)}")
        return {"status": "error", "reason": str(e)}
