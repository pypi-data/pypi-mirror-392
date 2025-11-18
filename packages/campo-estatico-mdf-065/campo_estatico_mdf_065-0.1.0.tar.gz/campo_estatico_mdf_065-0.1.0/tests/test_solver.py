import pytest
import numpy as np
from campo_estatico_mdf.solver import LaplaceSolver2D

def test_caso_trivial_cero_voltios():
    """
    Prueba el Caso Trivial (RNF2.2): todas las fronteras a 0V.
    El interior debe ser 0V.
    """
    N = 10
    solver = LaplaceSolver2D(N, v_izquierda=0, v_derecha=0, v_arriba=0, v_abajo=0)
    solver.resolver_jacobi(tolerancia=1e-8)
    
    # Verificar que toda la matriz V es (casi) cero
    assert np.allclose(solver.V, 0.0, atol=1e-7)

def test_convergencia_simple():
    """
    Prueba RNF2.2: Convergencia para un caso simple (ej. potencial lineal).
    Si V_izq=10V y V_der=0V, el centro deberia ser ~5V.
    """
    N = 20
    solver = LaplaceSolver2D(N, v_izquierda=10, v_derecha=0, v_arriba=0, v_abajo=0)
    solver.resolver_jacobi(tolerancia=1e-6)
    
    # Verificar el punto central (aproximado)
    # Nota: No sera exactamente 5 debido a los bordes 0V arriba/abajo
    centro_x = N // 2
    centro_y = N // 2
    assert 1.0 < solver.V[centro_y, centro_x] < 7.0 # Una prueba de cordura

def test_calculo_campo_lineal():
    """
    Prueba RNF2.3: Calculo del campo E para un potencial lineal conocido.
    Si V es lineal (V = -ax), E debe ser constante (E = a).
    """
    N = 10
    solver = LaplaceSolver2D(N, 0, 0, 0, 0) # Inicializador no importa aqui

    # Crear un potencial lineal manualmente: V(x) = 5*x
    x = np.linspace(0, N-1, N)
    solver.V = np.tile(x, (N, 1)) * 5 # V = 5*x
    
    Ex, Ey = solver.calcular_campo_e()
    
    # E = -grad(V) = -(d(5x)/dx) = -5
    # Ey debe ser 0, Ex debe ser -5 (en los puntos interiores)
    
    # np.gradient usa diferencias centradas, por lo que los bordes seran diferentes
    assert np.allclose(Ey, 0.0, atol=1e-7)
    assert np.allclose(Ex[1:-1, 1:-1], -5.0, atol=1e-7)
