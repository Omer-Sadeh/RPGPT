import concurrent.futures
from backend import DEBUG
import logging
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '(%(process)d): %(asctime)s - %(name)s [%(thread)d] - [%(levelname)s] - %(message)s',
        },
    },
    'handlers': {
        'file_handler': {
            'class': 'logging.FileHandler',
            'filename': 'backend/app.log',
            'formatter': 'default',
            'mode': 'w',
        }
    },
    'loggers': {
        '': {
            'handlers': ['file_handler'],
            'level': 'INFO' if not DEBUG else 'DEBUG',
            'propagate': False,
        },
        'uvicorn': {
            'handlers': ['file_handler'],
            'level': 'CRITICAL',
            'propagate': False,
        },
        'urllib3': {
            'level': 'WARNING',
            'handlers': ['file_handler'],
            'propagate': False,
        }
    },
}

async_context = concurrent.futures.ThreadPoolExecutor()
logging.config.dictConfig(LOGGING_CONFIG)


class CustomException(Exception):
    """
    custom exception class for specific error messages returned from the API.
    """


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
            return {"status": "success", "result": func(*args, **kwargs)}
        except CustomException as exc:
            logging.warning(f"Custom exception found in: {func.__name__}: {str(exc)}")
            return {"status": "error", "reason": str(exc)}
        except Exception as exc:
            logging.exception(f"exception found in: {func.__name__}:")
            return {"status": "error", "reason": "The server encountered an error while processing the request."}
    return wrapper


def APIEndpoint(func: callable) -> callable:
    """
    Wraps a function with logging statements to indicate the start and end of the function.
    The wrapped function logs the function name and the arguments passed to it.

    :param func: the function to be wrapped
    :return: the wrapped function
    """
    def wrapper(*args, **kwargs):
        logging.info(f"--------- API call: {func.__name__} started!")
        logging.debug(f"Arguments: {args}, {kwargs}")
        result = func(*args, **kwargs)
        logging.info(f"--------- API call: {func.__name__} finished!")
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
            logging.warning(f"An error occurred while executing the promise: {function.__name__}, {str(e)}")
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
