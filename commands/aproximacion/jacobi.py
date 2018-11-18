# -*- coding: UTF-8 -*-
"""
Implements the jacobi iterative method to solve the A.x=B equation.

Heavily inspired on:
    https://www.quantstart.com/articles/Jacobi-Method-in-Python-and-NumPy
"""

import numpy as np


def solve_by_jacobi(A, B, error_bound=0.001, x=None):
    """Solves the equation Ax=b via the Jacobi iterative method.

    See https://en.wikipedia.org/wiki/Jacobi_method for implementation details.

    The idea is decomposing A so that:
        A = D + R
    where D is a diagonal matrix and R the remainder (A - diag(A))
    With that notation we have:
        A.x = B
        (D+R).x = B
        D.x + R.x = B
        D.x = B - R.x
        D⁻¹.D.x = D⁻¹.(B - R.x)
        x = D⁻¹.(B - R.x)

    And with a bit of analysis we know that the product
        D⁻¹.(B - R.x)
    is the same as taking each element on (B - R.x) matrix and divide it
    by the inverse of the coefficient of the Aᵢᵢ element of the diagonal matrix.

    Args:
        A (np.array): Matrix A. It contains the coefficient of the incognitas
        B (np.array: Matrix B. It contains the result of each equation
        error_bound (float): Minimum acceptable error to the real answer. Once error is less than error_bound, stop calculating.
        x (list[int]): Initial vector guess (Optional)
    """
    np.seterr(all='raise')

    # Creates an initial guess if needed
    if x is None:
        x = np.zeros(len(A[0]))
    elif isinstance(x, list):
        x = np.array(x)

    # Create a vector of the diagonal elements of A
    D = np.diag(A)

    # Get the remainder matrix by substracting the diagonal
    R = A - np.diagflat(D)

    results = [(x, '-', '-', '-')]
    value_diff = error_bound + 1
    while not (value_diff <= error_bound):
        # x = (B - R.x) / D
        old_x = x
        x = (B - np.dot(R, x)) / D

        # Save step results
        norma_1 = norm_1(x - old_x)
        norma_2 = norm_2(x - old_x)
        norma_inf = infinite_norm(x - old_x)

        # Evaluate if we should continue. If value
        value_diff = norma_2
        results.append((x, norma_1, norma_2, norma_inf))

    return x, results


def infinite_norm(array):
    return np.linalg.norm(array, ord=np.inf)


def norm_1(array):
    return np.linalg.norm(array, ord=1)


def norm_2(array):
    return np.linalg.norm(array, ord=None)


"""
A = np.array([
    [5.0, -1.0, 3.0],
    [1.0, 6.0, -4],
    [-1.0, 2, -4.0],
])
b = np.array([3.0, 7.0, 1.0])
A = np.array([
    [3.0, 1.0],
    [0.0, 4.0]
])

b = np.array([1.0, 2.0])

sol, res = solve_by_jacobi(A, b, error_bound=0.0001)

np.set_printoptions(precision=10)

print("Solución (r): %s" % sol)
"""
