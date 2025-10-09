"""
Implementation of some functions for manipulations with generators:
Implementation of generator function that creates an iterator of prime numbers;
Implementation of pipeline function that applies the given operations sequentially to the input iterator;
Implementation of aggregate function that collects the pipeline result into a list.
implementation of custom function that squares elements of iterable objects.
"""

from math import isqrt
from typing import Iterator, Iterable, Any, Callable


def sieve_eratosthenes_generator(end: int) -> Iterator[int]:
    """
    Generator function that creates an iterator of prime numbers up to the given natural number according to the sieve of eratosthenes algorithm.

    Args:
        end: The natural number up to which the Sieve of Eratosthenes is considered

    Returns:
        An iterator of prime numbers up to the given natural number

    Raises:
        TypeError: If given argument is not a natural number
        ValueError: If given number is less than 2
    """

    if type(end) is not int:
        raise TypeError(
            f"Argument {end} type of {type(end).__name__} is not a natural number"
        )
    if end < 2:
        raise ValueError(
            f"The natural number up to which the Sieve of Eratosthenes is considered must be greater than or equal to 2; {end} is less than 2"
        )

    isPrime = [True] * (end + 1)
    isPrime[0], isPrime[1] = False, False

    for i in range(2, isqrt(end) + 1):
        if isPrime[i]:
            for j in range(i * i, end + 1, i):
                isPrime[j] = False

    for i in range(2, end + 1):
        if isPrime[i]:
            yield i


def pipeline(
    stream: Iterable[Any], operations: list[Callable[[Iterable[Any]], Iterable[Any]]]
) -> Iterator[Any]:
    """
    Pipeline function that applies the given operations sequentially to the input iterator.
    Given built-in iterable functions must be wrapped in lambda functions.

    Args:
        stream: The given iterator
        operations: The list of given operations

    Returns:
        An iterator of applied operations
    """

    current_stream: Iterable[Any] = stream

    for operation in operations:
        current_stream = operation(current_stream)

    return iter(current_stream)


def aggregate(stream: Iterable[Any]) -> list[Any]:
    """
    Aggregate function that collects the iterator elements into a list.

    Args:
        stream: The given iterator

    Returns:
        The list of elements from the given iterator
    """

    return list(stream)


def squaring(stream: Iterable[Any]) -> Iterator[Any]:
    """
    Custom function that squares elements of iterable objects.

    Args:
        stream: The given iterator

    Returns:
        An iterator of squared elements from given iterator

    Raises:
        TypeError: If elements of iterable object cannot be squared
    """

    def safe_squaring(x):
        try:
            return x**2
        except TypeError:
            raise TypeError(f"Element {x} type of {type(x).__name__} cannot be squared")

    return map(safe_squaring, stream)
