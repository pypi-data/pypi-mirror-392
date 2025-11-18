from typing import List

Matrix = List[List[float]]

def minor(matrix: Matrix, row: int, col: int) -> Matrix:
    """
    Calculates the minor of a matrix by removing the specified row and column.

    Args:
        matrix (Matrix): The input matrix.
        row (int): The row to remove, counting from 0.
        col (int): The column to remove, counting from 0.

    Returns:
        Matrix: The minor of the matrix.

    Example:
        ```python
        >>> minor([[1, 2, 3], [4, 5, 6], [7, 8, 9]], 1, 1)
        [[1, 3], [7, 9]]
        ```
    """
    return [
        [val for col_idx, val in enumerate(row) if col_idx != col]
        for row_idx, row in enumerate(matrix) if row_idx != row
    ]

def determinant(matrix: Matrix) -> float:
    """
        Recursively calculates the determinant of a matrix, using the Laplace expansion.

        Args:
            matrix (Matrix): The input matrix.

        Returns:
            float: The determinant of the matrix.
    """
    num_rows = len(matrix)
    if num_rows != len(matrix[0]):
        raise ValueError("Matrix is not quadratic.")

    if num_rows == 1:
        return matrix[0][0]
    if num_rows == 2:
        # Direktlösung für 2x2
        return matrix[0][0]*matrix[1][1] - matrix[0][1]*matrix[1][0]
    det = 0.0
    for col, val in enumerate(matrix[0]):
        sign = (-1) ** col
        det += sign * val * determinant(minor(matrix, 0, col))
    return det

def cofactor_matrix(matrix: Matrix) -> Matrix:
    """
        Calculates the cofactor matrix of a given matrix:
        1. Calculate the minor for each element.
        2. Multiply the minor by (-1)^(i+j) where i and j are the row and column indices of the element.
        3. Return the cofactor matrix.

    Args:
        matrix (Matrix): The input matrix.
    Returns:
        Matrix: The cofactor matrix.
    Raises:
        ValueError: If the matrix is not square.

    """
    n = len(matrix)
    if n != len(matrix[0]):
        raise ValueError("Matrix is not quadratic.")

    cofactors = []
    for i in range(n):
        row = []
        for j in range(n):
            sign = (-1) ** (i + j)
            row.append(sign * determinant(minor(matrix, i, j)))
        cofactors.append(row)
    return cofactors

def transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix)]

def inverse(matrix: Matrix) -> Matrix:
    """
        Calculates the inverse of a matrix using the adjugate method:
        1. Calculate the determinant of the matrix.
        2. Calculate the cofactor matrix.
        3. Transpose the cofactor matrix to get the adjugate matrix.
        4. Divide each element of the adjugate matrix by the determinant.

    Args:
        matrix (Matrix): The input matrix.
    Returns:
        Matrix: The inverse of the matrix.
    Raises:
        ValueError: If the matrix is not square or not invertible (determinant is zero).
    """
    det = determinant(matrix)
    if abs(det) < 1e-12:
        raise ValueError("Matrix is not invertible (determinant is zero).")
    cof = cofactor_matrix(matrix)
    adj = transpose(cof)
    return [[elem / det for elem in row] for row in adj]
