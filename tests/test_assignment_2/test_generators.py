import pytest
from project.assignment_2 import generators as g


def common_parametrize():
    return pytest.mark.parametrize(
        "input_stream, expected",
        [
            (range(5), range(5, 10)),
            ([0, 1, 2, 3, 4], [5, 6, 7, 8, 9]),
        ],
    )


@common_parametrize()
def test_aggregate(input_stream, expected):
    """Aggregate function test"""
    assert g.aggregate(input_stream) == expected
