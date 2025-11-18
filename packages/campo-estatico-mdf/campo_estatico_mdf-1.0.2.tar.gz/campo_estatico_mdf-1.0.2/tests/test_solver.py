# tests/test_solver.py
import numpy as np
from campo_estatico_mdf import LaplaceSolver2D

def _build_simple_problem(N=21):
    bc = {"left": 1.0, "right": 0.0, "top": 0.0, "bottom": 0.0}
    return dict(
        N=N,
        bc=bc,
        epsilon=1e-5,
        max_iter=50000,
    )

def test_gauss_seidel_runs_more_than_one_iteration():
    params = _build_simple_problem()
    # OJO: guion bajo, no guion
    solver = LaplaceSolver2D(method="gauss_seidel", **params)
    V, n_iter, err = solver.solve()

    # Si el problema no es trivial, no debería converger en 1 sola iteración
    assert n_iter > 1
    assert err >= 0.0


def test_gauss_seidel_close_to_jacobi_solution():
    params = _build_simple_problem(N=31)

    solver_jacobi = LaplaceSolver2D(method="jacobi", **params)
    V_j, n_iter_j, err_j = solver_jacobi.solve()

    # OJO: guion bajo, no guion
    solver_gs = LaplaceSolver2D(method="gauss_seidel", **params)
    V_gs, n_iter_gs, err_gs = solver_gs.solve()

    assert np.allclose(V_j, V_gs, atol=5e-3)
    assert n_iter_gs <= n_iter_j
