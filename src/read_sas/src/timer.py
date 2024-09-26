from functools import wraps
import time


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(
            f"Function:\t{func.__name__}\t\t | Execution time:\t{end_time - start_time} seconds"
        )
        return result

    return wrapper
