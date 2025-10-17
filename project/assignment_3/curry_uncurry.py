import functools as ft
from typing import Callable, Any


def curry_explicit(func: Callable[..., Any], arity: int) -> Callable[..., Any]:

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
