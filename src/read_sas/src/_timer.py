from functools import wraps
import time
from typing import Callable, TypeVar

T = TypeVar("T")


def timer(func: Callable[..., T]) -> Callable[..., T]:
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        if end_time - start_time > 3600:
            execution_time = f"{(end_time - start_time) / 3600:.2f} hours"
        elif end_time - start_time > 60:
            execution_time = f"{(end_time - start_time) / 60:.2f} minutes"
        elif end_time - start_time > 1:
            execution_time = f"{end_time - start_time:.2f} seconds"
        elif end_time - start_time > 1e-3:
            execution_time = f"{(end_time - start_time) * 1e3:.2f} milliseconds"
        else:
            execution_time = f"{(end_time - start_time) * 1e6:.2f} microseconds"

        print(f"Function:    {func.__name__}    | Execution time:    {execution_time}")  # noqa: T201
        return result

    return wrapper
