"""mitchallen.roll - A dice rolling random number generator."""

import random
from importlib.metadata import version

__version__ = version("mitchallen-roll")


def roll(sides: int = 6) -> int:
    """
    Return a random integer from 1 to sides (inclusive).

    Args:
        sides: Number of sides on the die (default: 6)

    Returns:
        int: Random integer from 1 to sides

    Raises:
        ValueError: If sides is less than 1

    Examples:
        >>> result = roll()
        >>> 1 <= result <= 6
        True
        >>> result = roll(20)
        >>> 1 <= result <= 20
        True
    """
    if sides < 1:
        raise ValueError("Number of sides must be at least 1")
    return random.randint(1, sides)


def d6() -> int:
    """
    Roll a 6-sided die.

    Returns:
        int: Random integer from 1 to 6

    Examples:
        >>> result = d6()
        >>> 1 <= result <= 6
        True
    """
    return roll(6)


def d20() -> int:
    """
    Roll a 20-sided die.

    Returns:
        int: Random integer from 1 to 20

    Examples:
        >>> result = d20()
        >>> 1 <= result <= 20
        True
    """
    return roll(20)


__all__ = ["roll", "d6", "d20"]
