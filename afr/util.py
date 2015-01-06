"""Various utility functions."""

import os


def clamp(i, minimum, maximum):
    """Clamp i so minimum<=i<=maximum."""
    if minimum > maximum:
        raise ValueError("Minimum must be equal to or less than maximum")
    return max(min(maximum, i), minimum)
