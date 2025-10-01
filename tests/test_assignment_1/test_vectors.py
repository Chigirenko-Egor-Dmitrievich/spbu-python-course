import pytest
from project.assignment_1 import vectors as v
from math import isclose

def test_scalar_product():
    """Scalar product test."""
    v1 = [3, 2, 1]
    v2 = [4, 5, 6]
    assert v.scalar_product(v1, v2) == 28


def test_error_scalar_product():
    """Error test for scalar product."""
    v1 = [1, 1, 1]
    v2 = [2, 2]
    with pytest.raises(ValueError):
        v.scalar_product(v1, v2)


def test_vector_length():
    """Length test."""
    assert v.length([1, 1, 1, 2, 3]) == 4.0


def test_angle_parallel_vectors():
    """Parallel vectors test."""
    v1 = [1, 2]
    v2 = [3, 6]
    assert isclose(v.angle(v1, v2), 0.0, abs_tol=1e-5)


def test_angle_orthogonal_vectors():
    """Orthogonal vectors test."""
    v1 = [1, -2]
    v2 = [2, 1]
    assert v.angle(v1, v2) == 90.0