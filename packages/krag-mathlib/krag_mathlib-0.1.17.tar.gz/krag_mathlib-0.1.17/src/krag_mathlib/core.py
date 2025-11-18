"""
krag_mathlib.core

A small collection of basic mathematical operations.
"""

import math
from typing import Union

Number = Union[int, float]


def add(a: Number, b: Number) -> Number:
    """Return the sum of two numbers."""
    return a + b


def subtract(a: Number, b: Number) -> Number:
    """Return the result of subtracting b from a."""
    return a - b


def multiply(a: Number, b: Number) -> Number:
    """Return the product of two numbers."""
    return a * b


def divide(a: Number, b: Number) -> Number:
    """Return the result of dividing a by b."""
    if b == 0:
        raise ZeroDivisionError("division by zero is not allowed")
    return a / b


def exponent(a: Number, b: Number) -> Number:
    """Return a raised to the power of b."""
    return a ** b


def log(value: Number, base: Number = math.e) -> float:
    """
    Return the logarithm of 'value' to the given base.
    Default base is e (natural logarithm).
    """
    if value <= 0:
        raise ValueError("logarithm undefined for non-positive values")
    if base <= 0 or base == 1:
        raise ValueError("invalid base for logarithm")
    return math.log(value, base)
