# coding=utf-8
"""
Collection of package management routines
"""

from __future__ import annotations

import warnings
import time
import functools

from swgoh_comlink.globals import get_logger

logger = get_logger(__name__)


class DeprecatedClass(type):
    """Metaclass to warn about deprecated classes"""
    def __getattribute__(cls, name):
        # Avoid warning for special methods/attributes used by Python itself
        if not name.startswith('__') or name in ['__class__', '__dict__', '__bases__', '__mro__']:
            replacement_class = cls.__replacement_class__ if hasattr(cls, '__replacement_class__') else 'Unknown'
            warnings.warn(
                    f"Class '{cls.__name__}' is deprecated. Use {replacement_class} instead.",
                    DeprecationWarning,
                    stacklevel=2
                    )
        return super().__getattribute__(name)


def retry(max_retries: int = 3, backoff: int = 2, exceptions: tuple = (Exception,)):
    """
    A decorator to retry a function's execution if specified exceptions occur.
    Beginning with the first retry, the delay between retries will increase exponentially,
    starting with a delay of 1 second.

    Args:
        max_retries (int): The maximum number of times to retry the function.
        backoff (int): The exponential backoff factor to apply between retries.
        exceptions (tuple): A tuple of exception types to catch and retry on.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            delay_seconds = 1
            while attempts < max_retries:
                if attempts > 0:
                    delay_seconds **= backoff
                    logger.debug(f"[{func.__name__}()] Retry delay increased to {delay_seconds} seconds.")
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempts += 1
                    logger.warning(f"[{func.__name__}()] Attempt {attempts} failed: {e}. Retrying in {delay_seconds} "
                                   f"seconds...")
                    time.sleep(delay_seconds)
            raise  # Re-raise the last exception if all retries fail
        return wrapper
    return decorator
