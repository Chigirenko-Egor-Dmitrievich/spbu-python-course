import pytest
from project.assignment_2 import generators as g
from typing import Iterator
from functools import reduce


def gen_lst() -> Iterator[list[int]]:
    """Function that returns an iterator of lists"""
    yield [1, 2, 3]
    yield [4, 5, 6]
    yield [7, 8, 9]


def gen_tpl() -> Iterator[tuple[str, int]]:
    """Function that returns an iterator of tuples"""
    yield ("1st", 1)
    yield ("2nd", 2)
    yield ("3rd", 3)


@pytest.mark.parametrize(
    "input_stream, collection, expected",
    [
        (range(5), list, [0, 1, 2, 3, 4]),
        (range(5, 10), str, "56789"),
        (gen_lst(), tuple, ([1, 2, 3], [4, 5, 6], [7, 8, 9])),
        ([1, 1, 2, 2, 3, 3], set, {1, 2, 3}),
        (gen_tpl(), dict, {"1st": 1, "2nd": 2, "3rd": 3}),
        (range(1, 5), dict, [1, 2, 3, 4]),
    ],
)
def test_aggregate(input_stream, collection, expected):
    """Aggregate function test"""
    assert g.aggregate(input_stream, collection) == expected


@pytest.mark.parametrize(
    "input_stream, expected",
    [
        (range(5), [0, 1, 4, 9, 16]),
        ([1, 2, 3], [1, 4, 9]),
    ],
)
def test_squaring(input_stream, expected):
    """Squaring function test"""
    assert g.aggregate(g.squaring(input_stream)) == expected


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
        g.aggregate(g.sieve_eratosthenes_generator(input_number))


def test_errorValue_sieve_eratosthenes_generator():
    """Generator function errorValue test"""
    input_number = -10
    with pytest.raises(ValueError):
        g.aggregate(g.sieve_eratosthenes_generator(input_number))


@pytest.mark.parametrize(
    "input_stream, operations, collection, expected",
    [
        (
            g.sieve_eratosthenes_generator(10),
            [
                (map, lambda x: x * 2),
                g.squaring,
            ],
            tuple,
            (16, 36, 100, 196),
        ),
        (
            range(5),
            [
                g.squaring,
                (filter, lambda x: x >= 8),
                (zip, ["1st", "2nd"]),
            ],
            dict,
            {"1st": 9, "2nd": 16},
        ),
        (
            [1, -1, 2, -2, 3, -3],
            [
                g.squaring,
                set,
                (reduce, lambda x, y: x + y),
                list,
            ],
            list,
            [14],
        ),
    ],
)
def test_pipeline(input_stream, operations, collection, expected):
    """Pipeline function test"""
    assert g.aggregate(g.pipeline(input_stream, operations), collection) == expected


@pytest.mark.parametrize(
    "input_stream, operations, expected",
    [
        (
            g.sieve_eratosthenes_generator(20),
            [
                (map, lambda x: x + 1),
                (filter, lambda x: x % 2 == 0),
                g.squaring,
                enumerate,
                (map, lambda x, y: (str(x), y)),
            ],
            [
                ("1", 16),
                ("2", 36),
                ("3", 64),
                ("4", 144),
                "the remaining elements of iterator have not been calculated yet",
            ],
        ),
    ],
)
def test_lazy_pipeline(input_stream, operations, expected):
    """Pipeline function lazy computation test"""
    temp = g.pipeline(input_stream, operations)
    assert [
        next(temp),
        next(temp),
        next(temp),
        next(temp),
        "the remaining elements of iterator have not been calculated yet",
    ] == expected
