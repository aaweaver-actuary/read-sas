import cProfile
import functools


class Profiler:
    def __init__(self):
        self.profiler = cProfile.Profile()

    def __enter__(self):
        self.profiler.enable()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.profiler.disable()
        self.profiler.print_stats(sort="tottime")

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self.profiler.enable()
            result = func(*args, **kwargs)
            self.profiler.disable()
            self.profiler.print_stats(sort="tottime")
            return result

        return wrapper

    def print_stats(self):
        self.profiler.print_stats(sort="tottime")

    def reset(self):
        self.profiler.clear_stats()
