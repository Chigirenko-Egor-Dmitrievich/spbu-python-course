import pytest
from project.assignment_1 import matrices as m


def test_check_addition_matrices():
    """Test of checking whether matrices match conditions for matrix addition."""
    m1 = [[1, 1], [2, 2]]
    m2 = [[3, 3], [4, 4]]
    assert m.check_matrices(m1, m2, "addition") == None


def test_check_multiplication_matrices():
    """Test of checking whether matrices match conditions for matrix multiplication."""
    m1 = [[1, 1, 1], [2, 2, 2]]
    m2 = [[3, 3], [4, 4], [5, 5]]
    assert m.check_matrices(m1, m2, "multiplication") == None


def test_error_check_matrices_definitions():
    """Error test of checking whether matrices match the definition of matrix."""
    m1 = [[1, 1], [2, 2]]
    m2 = [[3, 3], [4, 4, 4], [5, 5]]
    with pytest.raises(ValueError):
        m.check_matrices(m1, m2, "addition")


def test_error_check_addition_matrices():
    """Error test of checking whether matrices match conditions for matrix addition."""
    m1 = [[1, 1, 1], [2, 2, 2]]
    m2 = [[3, 3], [4, 4], [5, 5]]
    with pytest.raises(ValueError):
        m.check_matrices(m1, m2, "addition")


def test_error_check_multiplication_matrices():
    """Error test of checking whether matrices match conditions for matrix multiplication."""
    m1 = [[1, 1, 1, 1], [2, 2, 2, 2]]
    m2 = [[3, 3], [4, 4], [5, 5]]
    with pytest.raises(ValueError):
        m.check_matrices(m1, m2, "multiplication")


def test_addition_matrices():
    """Test of addition of two matrices."""
    m1 = [[1, 1], [2, 2]]
    m2 = [[3, 3], [4, 4]]
    assert m.add_matrices(m1, m2) == [[4, 4], [6, 6]]


def test_addition_rectangular_matrices():
    """Test of addition of two non-square matrices."""
    m1 = [[1, 1, 1], [2, 2, 2]]
    m2 = [[3, 3, 3], [4, 4, 4]]
    assert m.add_matrices(m1, m2) == [[4, 4, 4], [6, 6, 6]]


def test_error_addition_matrices():
    """Error test of addition of two matrices."""
    m1 = [[1, 1, 1], [2, 2, 2]]
    m2 = [[3, 3], [4, 4], [5, 5]]
    with pytest.raises(ValueError):
        m.add_matrices(m1, m2)


def test_multiplication_matrices():
    """Test of multiplication of two matrices."""
    m1 = [[1, 1], [2, 2]]
    m2 = [[3, 3], [4, 4]]
    assert m.multiply_matrices(m1, m2) == [[7, 7], [14, 14]]


def test_multiplication_rectangular_matrices():
    """Test of multiplication of two non-square matrices."""
    m1 = [[1, 1, 1], [2, 2, 2]]
    m2 = [[3, 3], [4, 4], [5, 5]]
    assert m.multiply_matrices(m1, m2) == [[12, 12], [24, 24]]


def test_error_multiplication_matrices():
    """Error test of multiplication of two matrices."""
    m1 = [[1, 1, 1, 1], [2, 2, 2, 2]]
    m2 = [[3, 3], [4, 4], [5, 5]]
    with pytest.raises(ValueError):
        m.multiply_matrices(m1, m2)


def test_transpose_matrix():
    """Matrix transposing test."""
    matrix = [[1, 2, 3], [4, 5, 6]]
    assert m.transpose_matrix(matrix) == [[1, 4], [2, 5], [3, 6]]


def test_transpose_vector():
    """Vector transposing test."""
    matrix = [[1, 2, 3, 4]]
    assert m.transpose_matrix(matrix) == [[1], [2], [3], [4]]


def test_double_transpose_matrix():
    """Matrix double transposing test."""
    matrix = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
    assert m.transpose_matrix(m.transpose_matrix(matrix)) == matrix
