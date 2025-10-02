import pytest
from project.assignment_1 import matrices as m

#def test_check_equal_sized_matrices():
#    """Test of equal-sized matrices"""
#    m1 = [[1, 2], [3, 4]]
#    m2 = [[5, 6], [7, 8]]
#    assert m.check_matrices(m1, m2) == True
#
#
#def test_check_differen_sized_matrices():
#    """Test of different-sized matrices"""
#    m1 = [[1, 2], [3, 4]]
#    m2 = [[1, 2]]
#    assert m.check_matrices(m1, m2) == False


def test_add_matrices_basic():
    """Test of addition of two matrices"""
    m1 = [[1, 2], [3, 4]]
    m2 = [[5, 6], [7, 8]]
    assert m.add_matrices(m1, m2) == [[6, 8], [10, 12]]


def test_add_matrices_error():
    """Test for error in matrix addition."""
    m1 = [[1, 2]]
    m2 = [[1, 2, 3]]
    with pytest.raises(ValueError):
        m.add_matrices(m1, m2)


def test_add_rectangular_matrices():
    """Test addition of non-square matrices."""
    m1 = [[1, 2, 3], [4, 5, 6]]
    m2 = [[7, 8, 9], [10, 11, 12]]
    assert m.add_matrices(m1, m2) == [[8, 10, 12], [14, 16, 18]]


def test_multiply_matrices_2x2():
    """Test of multiplication of two 2x2 matrices."""
    m1 = [[1, 2], [3, 4]]
    m2 = [[2, 0], [1, 2]]
    assert m.multiply_matrices(m1, m2) == [[4, 4], [10, 8]]


def test_multiply_matrices_2x3_and_3x2():
    """Test of multiplication of a 2x3 matrix by a 3x2 matrix."""
    m1 = [[1, 2, 3], [4, 5, 6]]
    m2 = [[7, 8], [9, 10], [11, 12]]
    assert m.multiply_matrices(m1, m2) == [[58, 64], [139, 154]]


def test_multiply_matrices_incompatible_error():
    """Incompatible matrix error test."""
    m1 = [[1, 2, 3]]
    m2 = [[1, 2]]
    with pytest.raises(ValueError):
        m.multiply_matrices(m1, m2)


def test_transpose_2x3():
    """2x3 matrix transpose test."""
    matrix = [[1, 2, 3], [4, 5, 6]]
    assert m.transpose_matrix(matrix) == [[1, 4], [2, 5], [3, 6]]


def test_transpose_single_row():
    """Row transpose test."""
    matrix = [[1, 2, 3, 4]]
    assert m.transpose_matrix(matrix) == [[1], [2], [3], [4]]


def test_transpose_double_transpose():
    """Double transposing test."""
    matrix = [[1, 2, 3], [4, 5, 6]]
    assert m.transpose_matrix(m.transpose_matrix(matrix)) == matrix