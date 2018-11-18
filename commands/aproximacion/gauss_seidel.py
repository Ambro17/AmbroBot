# -*- coding: UTF-8 -*-
"""
Implements the jacobi iterative method to solve the A.x=B equation.

Heavily inspired on:
    https://www.quantstart.com/articles/Jacobi-Method-in-Python-and-NumPy
"""

import numpy as np
from numpy.linalg import LinAlgError


def solve_by_gauss_seidel(A, B, error_bound=0.001, x=None):
    """Solves the equation Ax=b via the Gauss Seidel iterative method.

    See https://en.wikipedia.org/wiki/Gauss%E2%80%93Seidel_method for implementation details.

    The idea is decomposing A so that:
        A = L + U
    where L is the lower triangular matrix of A (It includes the diagonal)
    and U is the strictly upper triangular matrix deriving of A.
    With that notation we have:
        A.x = B
        (L+U).x = B
        L.x + U.x = B
        L.x = B - U.x
        L⁻¹.L.x = L⁻¹.(B - U.x)
        x = L⁻¹.(B - U.x)

    And with a bit of analysis we know that the product
        L⁻¹.(B - U.x)
    is the same as taking each element on (B - U.x) matrix and divide it
    by the inverse of Lᵢⱼ element of the matrix.
    """
    np.seterr(all='raise')

    # Creates an initial guess if needed
    if x is None:
        x = np.zeros(len(A[0]))
    elif isinstance(x, list):
        x = np.array(x)

    # Create a lower triangular matrix of A
    L = np.tril(A)
    # print("Matriz Triangular inferior:\n %s" % L)
    try:
        L_inverse = np.linalg.inv(L)
    except LinAlgError:
        raise ValueError(
            "La matriz triangular inferior de A no tiene inversa.\n"
            "Estás seguro que la matriz ingresada es diagonalmente dominante?"
        )

    # Get the strictly upper triangular matrix of A
    U = A - L

    # Iterate n times / n=iterations
    results = [(x, '-', '-', '-')]
    value_diff = error_bound + 1
    while not (value_diff <= error_bound):
        old_x = x
        # x = L⁻¹.(B - U.x)
        x = np.matmul(L_inverse, B - np.dot(U, x))

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

sol, res = solve_by_gauss_seidel(A, b, error_bound=0.0001, x=[1, 1, 1])

np.set_printoptions(precision=10)
pprint(res)
print("Solución (r): %s" % sol)



A = np.array([
                [6.0, 2.0, 1.0],
                [4.0, 8.0, 4.0],
                [1.0, -1, 5.0],
            ])
b = np.array([-1.0, 1.0, 2.0])

sol = solve_by_gauss_seidel(A, b, iterations=70)

np.set_printoptions(precision=10)
print("Solución (r): %s" % sol)
"""
