"""
Implementation of vector operations:
Scalar product of two vectors;
Vector length calculation;
Angle between two vectors calculation.
(Functions are used)
"""

from math import pi, acos


def scalar_product(vector_1: list[float], vector_2: list[float]) -> float:
    """
    Calculates the scalar product of two vectors.

    Args:
        vector_1: First given vector
        vector_2: Second given vector

    Returns:
        Scalar product of the two given vectors

    Raises:
        ValueError: If vectors have different lengths
    """

    if len(vector_1) != len(vector_2):
        raise ValueError("Error: Vectors lengths are not equal")

    return sum([vector_1[i] * vector_2[i] for i in range(len(vector_1))])


def length(vector: list[float]) -> float:
    """
    Calculates the length of a vector.

    Args:
        vector: Given vector

    Returns:
        Length of given vector
    """

    return sum([i**2 for i in vector]) ** 0.5


def angle(vector_1: list[float], vector_2: list[float]) -> float:
    """
    Calculates the angle between two vectors.

    Args:
        vector_1: First given vector
        vector_2: Second given vector

    Returns:
        Angle between two given vectors

    Raises:
        ValueError: If vectors have different lengths
    """

    if len(vector_1) != len(vector_2):
        raise ValueError("Error: Vectors lengths are not equal")

    return (180 * acos(scalar_product(vector_1, vector_2) / length(vector_1) / length(vector_2)) / pi)
