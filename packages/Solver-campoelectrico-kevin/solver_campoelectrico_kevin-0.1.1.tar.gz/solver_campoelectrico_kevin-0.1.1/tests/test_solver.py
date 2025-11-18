import numpy as np
import pytest
from campo_estatico_mdf.solver import LaplaceSolver2D

def test_trivial_case():
    """
    Prueba el caso trivial donde todas las fronteras son 0V.
    El potencial en el interior debe ser 0V.
    """
    solver = LaplaceSolver2D(N=10, V_top=0, V_bottom=0, V_left=0, V_right=0)
    solver.solve_jacobi(tol=1e-8)
    assert np.allclose(solver.V[1:-1, 1:-1], 0, atol=1e-7)

def test_convergence():
    """
    Prueba que el solver converge para un caso no trivial
    en un número razonable de iteraciones.
    """
    solver = LaplaceSolver2D(N=10, V_left=10, V_right=10, V_top=0, V_bottom=0)
    iterations = solver.solve_jacobi(tol=1e-5, max_iter=5000)
    assert iterations < 5000, "El solver no convergió."
    assert iterations > 10, "La convergencia fue demasiado rápida, podría ser un error."

def test_linear_potential_electric_field():
    """
    Verifica el cálculo del campo eléctrico para un potencial lineal conocido.
    Si V(x) = C*x, entonces E = -grad(V) = (-C, 0).
    """
    N = 20
    V_left = 0.0
    V_right = 10.0
    solver = LaplaceSolver2D(N=N, V_left=V_left, V_right=V_right)
    
    # Forzamos un potencial perfectamente lineal para la prueba
    for i in range(N):
        solver.V[:, i] = (V_right / (N - 1)) * i

    Ex, Ey = solver.calculate_electric_field()

    assert np.allclose(Ey, 0, atol=1e-5)
    
    expected_Ex = -(V_right - V_left) / (N - 1)
    assert np.allclose(Ex[1:-1, 1:-1], expected_Ex, atol=0.1)
