"""
Advanced function decorators for caching and smart argument processing.

This module provides decorators for function caching with configurable limits and intelligent handling of default argument evaluation and isolation.
"""

import functools as ft
import inspect
import copy
from collections import OrderedDict
from typing import Any, Callable, Optional, Hashable


def cache_function(
    _func: Optional[Callable] = None, *, limit: int = 0
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Cache function results with configurable size limit and automatic cleanup.

    Args:
        _func: Function to decorate (for decorator without parentheses)
        limit: Maximum cache size (0 = no caching)

    Returns:
        Decorated function with caching behavior

    Note:
        Automatically handles unhashable types and provides cache statistics
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:

        if limit <= 0:
            return func

        cache: OrderedDict[Hashable, Any] = OrderedDict()

        @ft.wraps(func)
        def inner(*args: Any, **kwargs: Any) -> Any:
            key: tuple[tuple[Any, ...], tuple[tuple[str, Any]]]

            try:
                check = hash(args)
                key = (args, tuple(sorted(kwargs.items())))
            except TypeError:
                hashable_args = list(args)
                for i in range(len(hashable_args)):
                    match i:
                        case _ if type(hashable_args[i]) is list:
                            hashable_args[i] = tuple(hashable_args[i])
                        case _ if type(hashable_args[i]) is dict:
                            hashable_args[i] = tuple(hashable_args[i].items())
                        case _ if type(hashable_args[i]) is set:
                            hashable_args[i] = frozenset(hashable_args[i])
                        case _ if type(hashable_args[i]) is bytearray:
                            hashable_args[i] = tuple(hashable_args[i])
                hashable_args_tpl = tuple(hashable_args)
                key = (hashable_args_tpl, tuple(sorted(kwargs.items())))

            if key in cache:
                cache.move_to_end(key)
                print(f"Returning {cache[key]} from cache")
                return cache[key]

            result = func(*args, **kwargs)

            if len(cache) >= limit:
                temp = cache.popitem(last=False)
                print(f"Removing the oldest element: {temp}")

            cache[key] = result
            print(f"Adding new element: {key} ---> {result}")

            return result

        return inner

    if callable(_func):
        return decorator(_func)

    return decorator


class Evaluated:
    """
    Marker for deferred evaluation of default arguments.

    When used as a default value, the wrapped function will be called to generate the actual default value at call time.
    """

    def __init__(self, func: Callable[..., Any]) -> None:
        self.func = func


class Isolated:
    """
    Marker for deep copy isolation of argument values.

    When used as a default value, the argument will be deep copied to prevent mutable argument sharing between calls.
    """

    pass


def smart_args(
    _func: Optional[Callable] = None, *, allow_pos_args: bool = True
) -> Callable[..., Any]:
    """
    Enhance function arguments with deferred evaluation and isolation.

    Args:
        _func: Function to decorate (for decorator without parentheses)
        allow_pos_args: Whether to process positional arguments

    Returns:
        Decorated function with enhanced argument handling

    Features:
        - Deferred evaluation of default values using Evaluated
        - Deep copy isolation using Isolated
        - Runtime validation of argument combinations
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        spec = inspect.getfullargspec(func)

        @ft.wraps(func)
        def inner(*args: Any, **kwargs: Any) -> Any:
            def_kwargs = spec.kwonlydefaults
            if def_kwargs:
                for kw in def_kwargs:

                    if (
                        type(def_kwargs[kw]) == Evaluated
                        and def_kwargs[kw].func == Isolated
                    ):
                        assert (
                            False
                        ), "It is forbidden to combine Evaluated and Isolated"

                    if type(def_kwargs[kw]) == Evaluated and kw not in kwargs:
                        kwargs[kw] = def_kwargs[kw].func()
                    elif type(def_kwargs[kw]) == Isolated:
                        if kw in kwargs:
                            kwargs[kw] = copy.deepcopy(kwargs[kw])
                        else:
                            raise ValueError(
                                "A keyword argument with default value Isolated has not been passed"
                            )
            if allow_pos_args:
                args_lst = list(args)
                spec_args = list(spec.args)
                spec_defaults = list(spec.defaults) if spec.defaults else []
                start = len(args_lst) - (len(spec_args) - len(spec_defaults))

                for i in range(start, len(spec_defaults)):
                    if isinstance(spec_defaults[i], Evaluated) and isinstance(
                        spec_defaults[i].func, Isolated
                    ):
                        assert (
                            False
                        ), "It is forbidden to combine Evaluated and Isolated"

                    if isinstance(spec_defaults[i], Evaluated):
                        args_lst.append(spec_defaults[i].func())
                    elif isinstance(spec_defaults[i], Isolated):
                        raise ValueError(
                            "A positional argument with default value Isolated has not been passed"
                        )
                    else:
                        args_lst.append(spec_defaults[i])

                delta = len(spec_args) - len(spec_defaults)
                for i in range(start):
                    if isinstance(spec_defaults[i], Isolated):
                        args_lst[delta + i] = copy.deepcopy(args_lst[delta + i])
                args = tuple(args_lst)

            return func(*args, **kwargs)

        return inner

    if callable(_func):
        return decorator(_func)

    return decorator
