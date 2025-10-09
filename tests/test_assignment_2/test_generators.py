import pytest
from project.assignment_2 import generators as g
from typing import Iterator
from functools import reduce


def gen() -> Iterator[list[int]]:
    """Function that returns an iterator of lists"""
    yield [1, 2, 3]
    yield [4, 5, 6]
    yield [7, 8, 9]


@pytest.mark.parametrize(
    "input_stream, expected",
    [
        (range(5), [0, 1, 2, 3, 4]),
        (map(str, range(5, 10)), ["5", "6", "7", "8", "9"]),
        (gen(), [[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
        ([1, 2, 3], [1, 2, 3]),
    ],
)
def test_aggregate(input_stream, expected):
    """Aggregate function test"""
    assert g.aggregate(input_stream) == expected


@pytest.mark.parametrize(
    "input_stream, expected",
    [
        (range(5), [0, 1, 4, 9, 16]),
        ([1, 2, 3], [1, 4, 9]),
    ],
)
def test_squaring(input_stream, expected):
    """Squaring function test"""
    assert g.squaring(input_stream) == expected


def test_error_squaring():
    """Squaring function error test"""
    input_stream = map(str, range(5, 10))
    with pytest.raises(TypeError):
        g.aggregate(g.squaring(input_stream))


@pytest.mark.parametrize(
    "input_number, expected",
    [
        (10, [2, 3, 5, 7]),
        (50, [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]),
        (
            100,
            [
                2,
                3,
                5,
                7,
                11,
                13,
                17,
                19,
                23,
                29,
                31,
                37,
                41,
                43,
                47,
                53,
                59,
                61,
                67,
                71,
                73,
                79,
                83,
                89,
                97,
            ],
        ),
    ],
)
def test_sieve_eratosthenes_generator(input_number, expected):
    """Generator function test"""
    assert g.aggregate(g.sieve_eratosthenes_generator(input_number)) == expected


def test_errorType_sieve_eratosthenes_generator():
    """Generator function errorType test"""
    input_number = "10"
    with pytest.raises(TypeError):
        g.sieve_eratosthenes_generator(input_number)


def test_errorValue_sieve_eratosthenes_generator():
    """Generator function errorValue test"""
    input_number = -10
    with pytest.raises(ValueError):
        g.sieve_eratosthenes_generator(input_number)


@pytest.mark.parametrize(
    "input_stream, operations, expected",
    [
        (
            g.sieve_eratosthenes_generator(10),
            [lambda x: map(lambda y: y * 2, x), g.squaring],
            [16, 36, 100, 196],
        ),
        (
            range(5),
            [
                g.squaring,
                lambda x: filter(lambda y: y >= 8, x),
                lambda x: zip(["1st", "2nd"], x),
            ],
            [("1st", 9), ("2nd", 16)],
        ),
        (
            [1, 2, 3],
            [g.squaring, iter([lambda x: reduce(lambda y, z: y + z, x)])],
            [14],
        ),
    ],
)
def test_pipeline(input_stream, operations, expected):
    """Pipeline function test"""
    assert g.aggregate(g.pipeline(input_stream, operations)) == expected
