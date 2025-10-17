"""
Explicit function currying and uncurrying utilities.

This module provides functions to transform functions between their normal and curried forms with explicit control over arity.
"""


import functools as ft
from typing import Callable, Any


def curry_explicit(func: Callable[..., Any], arity: int) -> Callable[..., Any]:
    """
    Convert a function into its curried version with explicit arity.

    Args:
        func: The function to curry
        arity: Number of arguments the function expects

    Returns:
        Curried version of the input function

    Raises:
        ValueError: If arity is negative
    """

    if arity < 0:
        raise ValueError("Arity must be a non-negative number")

    if arity == 0:
        return func

    @ft.wraps(func)
    def curried_implicit(arg: Any, /) -> Any:

        if arity == 1:
            return func(arg)
        return curry_explicit(lambda *args: func(arg, *args), arity - 1)

    return curried_implicit


def uncurry_explicit(func: Callable[..., Any], arity: int) -> Callable[..., Any]:
    """
    Convert a curried function back to its normal form with explicit arity.

    Args:
        func: The curried function to uncurry
        arity: Number of arguments the original function expected

    Returns:
        Uncurried version of the input function

    Raises:
        ValueError: If arity is negative or wrong number of arguments provided
    """

    if arity < 0:
        raise ValueError("Arity must be a non-negative number")

    @ft.wraps(func)
    def uncurried_implicit(*args: Any) -> Any:

        if len(args) != arity:
            first_word = "argument" if arity == 1 else "arguments"
            second_word = "argument is" if len(args) == 1 else "arguments are"
            raise ValueError(
                f"The curried function expects {arity} "
                + f"{first_word}, but {len(args)} "
                + f"{second_word} given"
            )

        original_function = func

        if arity == 0:
            original_function = original_function()

        for arg in args:
            original_function = original_function(arg)

        return original_function

    return uncurried_implicit
