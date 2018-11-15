import numpy as np
import pytest

from commands.aproximacion.gauss_seidel import solve_by_gauss_seidel
from commands.aproximacion.jacobi import solve_by_jacobi


@pytest.mark.parametrize("A, B, expected_solution", [
    (
            np.array([
                [9.0, 3.0],
                [2.0, 7.0]
            ]),
            np.array([1.0, 2.0]),
            [0.0175438596, 0.2807017544]
    ),
    (
            np.array([
                [4.0, 1.0],
                [1.5, 2.0]
            ]),
            np.array([0.0, 3.0]),
            [-0.4615384615, 1.8461538462]
    ),
    (
            np.array([
                [2.0, 0.0],
                [3.5, 5.0]]
            ),
            np.array([1.0, 10.0]),
            [0.5, 1.65]
    ),
    (
            np.array([
                [5.0, 2.0],
                [3.0, 4.0]]
            ),
            np.array([2.0, 3.0]),
            [0.1428571428, 0.6428571429]
    ),
    (
            np.array([
                [3.0, -2.0],
                [0.0, 2.0]]
            ),
            np.array([2.0, 3.0]),
            [1.6666666667, 1.5]
    ),
    (
            np.array([
                [10.0, -5.0],
                [4.0, 5.0]]
            ),
            np.array([2.0, 3.0]),
            [0.3571428477, 0.3142857218]
    ),
    (
            np.array([
                [-10.0, 2.0],
                [3.0, -11.0]]
            ),
            np.array([5.0, -2.0]),
            [-0.4903846154, 0.0480769231]
    ),
    (
            np.array([
                [3.0, 1.0],
                [1.0, 10.0]]
            ),
            np.array([-20.0, 50.0]),
            [-8.6206896552, 5.8620689655]
    ),
    (
            np.array([
                [5.0, -1.0, 3.0],
                [1.0, 6.0, -4],
                [-1.0, 2, -4.0],
            ]),
            np.array([3.0, 7.0, 1.0]),
            [0.75, 1.125, 0.125]
    ),
    (
            np.array([
                [-10.0, 1.0, 2.0],
                [-3.0, 30.0, 1],
                [2.0, 5, 10.0],
            ]),
            np.array([-8.0, 1.0, 9.0]),
            [0.94230769, 0.10560625, 0.65873533]
    ),
    (
            np.array([
                [6.0, 2.0, 1.0],
                [4.0, 8.0, 4.0],
                [1.0, -1, 5.0],
            ]),
            np.array([-1.0, 1.0, 2.0]),
            [-0.25, 0.0227272727, 0.4545454545]
    ),
])
def test_methods_give_correct_solution(A, B, expected_solution):
    np.testing.assert_allclose(
        solve_by_gauss_seidel(A, B, iterations=50),
        expected_solution
    )
    np.testing.assert_allclose(
        solve_by_jacobi(A, B, iterations=50),
        expected_solution
    )