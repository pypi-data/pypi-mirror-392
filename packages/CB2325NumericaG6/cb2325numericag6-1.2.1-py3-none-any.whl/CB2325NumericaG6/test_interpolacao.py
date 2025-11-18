import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from CB2325NumericaG6.interpolacao import (
    hermite_interp,
    poly_interp,
    linear_interp,
    PiecewiseLinearFunction,
)
def test_poly_interp_basic():
    x = [0, 1, 2]
    y = [1, 3, 7]
    f = poly_interp(x, y)
    assert round(f(1.5), 2) == 4.75   # P(x)=x²+x+1 → f(1.5)=4.75
    assert f(0) == 1
    assert f(1) == 3
    assert f(2) == 7
    
def test_poly_interp_invalid_inputs():
    with pytest.raises(ValueError):
        poly_interp([1], [2])
    with pytest.raises(ValueError):
        poly_interp([1,2,3], [2,3])  #tamanhos diferentes


def test_linear_interp_and_piecewise_eval():
    x = [0, 2, 4]
    y = [0, 4, 8]
    f = linear_interp(x, y)
    assert f(1) == 2
    assert f(3) == 6
    assert f(0) == 0
    assert f(4) == 8

def test_linear_interp_invalid_inputs():
    with pytest.raises(ValueError):
        linear_interp([0], [1])
    with pytest.raises(ValueError):
        linear_interp([0,1,2], [1,2])  #tamanhos diferentes


def test_piecewise_prime_inside_interval():
    x = [0, 1, 2]
    y = [1, 3, 5]
    f = PiecewiseLinearFunction(x, y)
    assert f.prime(0.5) == 2
    assert f.prime(1.5) == 2

def test_piecewise_prime_out_of_domain():
    x = [0, 1]
    y = [1, 3]
    f = PiecewiseLinearFunction(x, y)
    with pytest.raises(ValueError):
        f.prime(-0.1)
    with pytest.raises(ValueError):
        f.prime(1.0) # nos de interpolação:derivada indefinida

def test_piecewise_criar_segmento_polinomial():
    x1, x2 = 0, 2
    y1, y2 = 1, 5
    f = PiecewiseLinearFunction([x1, x2], [y1, y2])
    pol = f.criar_segmento_polinomial(x1, x2, y1, y2)
    # o polinômio é P(x)=2x+1
    assert abs(pol(0) - 1) < 1e-10
    assert abs(pol(1) - 3) < 1e-10
    assert abs(pol(2) - 5) < 1e-10
    with pytest.raises(ValueError):
        f.criar_segmento_polinomial(1,1,2,2)  # x1==x2 -→ erro

def test_piecewise_encontrar_segmentos_raiz():
    x = [0, 1, 2, 3]
    y = [1, -1, 2, -2]
    f = PiecewiseLinearFunction(x, y)
    roots = f.encontrar_segmentos_raiz()
    # Deve haver mudança de sinal em [0,1] e [2,3]
    assert (0,1) in roots
    assert (2,3) in roots

def test_piecewise_encontrar_segmentos_raiz_with_zeros():
    x = [0, 1, 2]
    y = [0, 2, 0]
    f = PiecewiseLinearFunction(x, y)
    roots = f.encontrar_segmentos_raiz()
    # O ponto 0 e 2 são raízes exatas
    assert (0,0) in roots
    assert (2,2) in roots

def test_hermite_interp_basic():
    x = [0, 1]
    y = [1, 2]
    dy = [0, 0]
    f = hermite_interp(x, y, dy)
    assert abs(f(0.5) - 1.5) < 0.1

def test_hermite_interp_invalid():
    with pytest.raises(ValueError):
        hermite_interp([0,1], [1], [0])
    with pytest.raises(ValueError):
        hermite_interp([0], [1], [1])
