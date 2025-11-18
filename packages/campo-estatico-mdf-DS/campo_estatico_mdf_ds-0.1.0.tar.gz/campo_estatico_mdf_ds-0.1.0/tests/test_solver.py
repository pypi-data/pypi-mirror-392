# tests/test_solver.py
import numpy as np
import pytest
from campo_estatico_mdf.solver import LaplaceSolver2D

def test_caso_trivial():
    """
    Prueba que si todas las fronteras son 0V, la solución es 0V en todas partes.
    """
    solver = LaplaceSolver2D(N=10, V_izq=0, V_der=0, V_sup=0, V_inf=0)
    solver.aplicar_condiciones_contorno()
    V, _ = solver.resolver_gauss_seidel()
    assert np.allclose(V, 0)

def test_convergencia_simple():
    """
    Prueba la convergencia con un caso simple: un lado a 10V y el resto a 0V.
    La solución no debe ser cero en el interior.
    """
    solver = LaplaceSolver2D(N=10, V_izq=10, V_der=0, V_sup=0, V_inf=0)
    solver.aplicar_condiciones_contorno()
    V, iteraciones = solver.resolver_gauss_seidel()

    assert iteraciones > 0
    assert not np.allclose(V[1:-1, 1:-1], 0)
    assert np.isclose(np.max(V), 10)

def test_campo_electrico_constante():
    """
    Prueba que para un potencial lineal, el campo eléctrico es constante.
    Ejemplo: V(x) = k*x -> E = -k
    """
    N = 20
    V_izq = 10
    V_der = 0

    solver = LaplaceSolver2D(N=N, V_izq=V_izq, V_der=V_der, V_sup=0, V_inf=0)

    # Creamos un potencial 2D que es lineal solo en la dirección x
    linspace = np.linspace(V_izq, V_der, N)
    solver.V = np.tile(linspace, (N, 1))

    Ex, Ey = solver.calcular_campo_e()

    # El campo Ey debería ser cero porque el potencial no varía en y
    assert np.allclose(Ey, 0)

    # El campo Ex debería ser constante y negativo
    valor_esperado_ex = -(V_der - V_izq) / (N - 1)

    # Verificamos que Ex es aproximadamente constante
    assert np.allclose(Ex, valor_esperado_ex, atol=1e-9)

def test_convergencia_dos_lados():
    """
    Prueba la convergencia con dos lados a 10V y dos a 0V.
    La solución debe ser simétrica y no trivial.
    """
    solver = LaplaceSolver2D(N=10, V_izq=10, V_der=10, V_sup=0, V_inf=0)
    solver.aplicar_condiciones_contorno()
    V, iteraciones = solver.resolver_gauss_seidel()

    assert iteraciones > 0
    assert not np.allclose(V[1:-1, 1:-1], 0)
    assert np.isclose(np.max(V), 10)
    assert np.isclose(np.min(V), 0)
    # Verifica la simetría a lo largo del eje y (horizontal)
    assert np.allclose(V, V[::-1, :])
