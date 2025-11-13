import time
import functools

def measure_duration(func):
    """
    Function decorator to measure the duration of a function call.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start_time
        return result, duration
    return wrapper