import functools
import time

from logging_module.log_config import insighter_logger


def ameasure_time(func):
    """
    Measures the execution time of an async function.

    Args:
        func: The async function to measure.

    Returns:
        The decorated async function or an object containing the time and result.
    """

    # noinspection PyCompatibility
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        insighter_logger.info(f"Time to execute {func.__name__}: {end_time - start_time}")
        return result

    return wrapper
