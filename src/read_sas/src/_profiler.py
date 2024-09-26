import cProfile
import functools
import threading


class Profiler:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(Profiler, cls).__new__(cls)
                    cls._instance.profiler = cProfile.Profile()
        return cls._instance

    def __enter__(self):
        self.profiler.enable()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.profiler.disable()
        self.profiler.print_stats(sort="tottime")

    def print_stats(self, sort="tottime", file=None):
        self.profiler.print_stats(sort=sort, stream=file)

    def reset(self):
        self.profiler.clear_stats()

    def profile(self, sort="tottime", file=None):
        """Decorator to profile a function."""

        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                self.profiler.enable()
                result = func(*args, **kwargs)
                self.profiler.disable()
                self.print_stats(sort=sort, file=file)
                return result

            return wrapper

        return decorator


class Profiler2:
    def __init__(self):
        self.profiler = cProfile.Profile()

    def __enter__(self):
        self.profiler.enable()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.profiler.disable()
        self.profiler.print_stats(sort="tottime")

    def print_stats(self):
        self.profiler.print_stats(sort="tottime")

    def reset(self):
        self.profiler.clear_stats()

    def profile(self, func):
        """Decorator to profile a function."""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self.profiler.enable()
            result = func(*args, **kwargs)
            self.profiler.disable()
            self.profiler.print_stats(sort="tottime")
            return result

        return wrapper
