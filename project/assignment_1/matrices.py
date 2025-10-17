"""
Implementation of matrix operations:
Addition of two matrices;
Multiplication of two matrices;
Matrix transposition.
(Functions are used).
"""


def check_matrices(
    matrix_1: list[list[float]], matrix_2: list[list[float]], operation: str
) -> None:
    """
    Checks whether the given matrices are rectangular i.e. match the definition of matrix.
    Checks whether the given matrices are match conditions for matrix addition or multiplication.

    Args:
        matrix_1: First given matrix
        matrix_2: Second given matrix
        operation: The name of operation: addition or multiplication

    Returns:
        True if matrices match all conditions above

    Raises:
        ValueError: If matrices do not match any conditions above
    """

    if any(
        len(matrix_1[i]) != len(matrix_1[i + 1]) for i in range(len(matrix_1) - 1)
    ) or any(
        len(matrix_2[i]) != len(matrix_2[i + 1]) for i in range(len(matrix_2) - 1)
    ):
        raise ValueError("One or both matrices do not match the definition of matrix")

    if (operation == "addition") and (
        (len(matrix_1) != len(matrix_2)) or (len(matrix_1[0]) != len(matrix_2[0]))
    ):
        raise ValueError("Invalid conditions for matrix addition")

    if (operation == "multiplication") and (len(matrix_1[0]) != len(matrix_2)):
        raise ValueError("Invalid conditions for matrix multiplication")

    return None


def add_matrices(
    matrix_1: list[list[float]], matrix_2: list[list[float]]
) -> list[list[float]]:
    """
    implements matrix addition.
    Matrix addition condition: both matrices are equal in size.

    Args:
        matrix_1: First given matrix
        matrix_2: Second given matrix

    Returns:
        Result of matrix addition
    """

    check_matrices(matrix_1, matrix_2, "addition")

    return [
        [matrix_1[i][j] + matrix_2[i][j] for j in range(len(matrix_1[0]))]
        for i in range(len(matrix_1))
    ]


def multiply_matrices(
    matrix_1: list[list[float]], matrix_2: list[list[float]]
) -> list[list[float]]:
    """
    implements matrix multiplication.
    Matrix multiplication condition: The length of the first matrix is equal to the width of the second matrix.

    Args:
        matrix_1: First given matrix
        matrix_2: Second given matrix

    Returns:
        Result of matrix multiplication
    """

    check_matrices(matrix_1, matrix_2, "multiplication")

    return [
        [
            sum([matrix_1[i][k] * matrix_2[k][j] for k in range(len(matrix_2))])
            for j in range(len(matrix_2[0]))
        ]
        for i in range(len(matrix_1))
    ]


def transpose_matrix(matrix: list[list[float]]) -> list[list[float]]:
    """
    Transposes a matrix.

    Args:
        matrix: Given matrix

    Returns:
        Transposed matrix
    """

    length = len(matrix)
    width = len(matrix[0])
    return [[matrix[j][i] for j in range(length)] for i in range(width)]
