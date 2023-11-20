import concurrent.futures
async_context = concurrent.futures.ThreadPoolExecutor()

DEBUG = True

def error_wrapper(func):
    def wrapper(*args, **kwargs):
        try:
            return {"status": "success","result": func(*args, **kwargs)}
        except Exception as exc:
            if DEBUG:
                return {"status": "error","reason": str(exc)}
            return {"status": "error","reason": "An error has occurred!"}
    return wrapper


def start_promise(function, *args, **kwargs):
    def handle_exception(promise):
        try:
            promise.result() # Attempt to receive the function's result
        except Exception as _:
            pass
    
    promise = async_context.submit(function, *args, **kwargs)
    promise.add_done_callback(handle_exception)
    return promise


def await_promise(promise):
    try:
        return promise.result()
    except Exception as e:
        return {"status": "error", "reason": str(e)}