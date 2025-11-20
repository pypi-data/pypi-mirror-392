"""mitchallen.coin - A simple coin flip random number generator."""

import random
from importlib.metadata import version

__version__ = version("mitchallen-coin")


def flip() -> bool:
    """
    Return a random boolean value with 50% probability for True or False.

    Returns:
        bool: True or False with equal probability

    Examples:
        >>> result = flip()
        >>> isinstance(result, bool)
        True
    """
    return random.random() > 0.5


def heads() -> bool:
    """
    Return a random boolean value (same as flip()).

    Returns:
        bool: True or False with equal probability

    Examples:
        >>> result = heads()
        >>> isinstance(result, bool)
        True
    """
    return flip()


def tails() -> bool:
    """
    Return the opposite boolean value of heads().

    Returns:
        bool: True if heads() would return False, False if heads() would return True

    Examples:
        >>> result = tails()
        >>> isinstance(result, bool)
        True
    """
    return not heads()


__all__ = ["flip", "heads", "tails"]
