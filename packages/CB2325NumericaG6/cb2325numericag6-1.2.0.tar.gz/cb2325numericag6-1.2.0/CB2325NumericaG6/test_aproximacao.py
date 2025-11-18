import numpy as np
import pytest

from CB2325NumericaG6.aproximacao import ajuste_linear, ajuste_polinomial
from CB2325NumericaG6.polinomios import Polinomio


# ----------------------
# ajuste linear: casos exatos
# ----------------------

def test_ajuste_linear_reta_exata():
    x = [0, 1, 2, 3]
    y = [1, 3, 5, 7]   # 2x + 1
    P = ajuste_linear(x, y)
    assert P[0] == pytest.approx(2.0, rel=1e-12)
    assert P[1] == pytest.approx(1.0, rel=1e-12)


# ----------------------
# ajuste polinomial: convergência
# ----------------------
@pytest.mark.parametrize("n, tol", [(10, 5e-3), (100, 5e-4), (1000, 5e-5)])
def test_ajuste_polinomial_quadratico_converge(n, tol):
    f = lambda x: x*x
    x = np.linspace(0, 1, n + 1)
    y = f(x)
    P = ajuste_polinomial(x, y, n=2)
    assert P(0.5) == pytest.approx(0.25, abs=tol)


# ----------------------
# grau 3 exato
# ----------------------
def test_ajuste_polinomial_grau_3_exato():
    f = lambda x: x**3 - x + 1
    x = [0, 1, 2, 3]
    y = [f(t) for t in x]
    P = ajuste_polinomial(x, y, n=3)
    xs = np.linspace(0, 3, 7)
    for t in xs:
        assert P(t) == pytest.approx(f(t), rel=1e-12)


# ----------------------
# erros esperados
# ----------------------
def test_ajuste_linear_tamanho_invalido():
    with pytest.raises(ValueError):
        ajuste_linear([1, 2], [5])


def test_ajuste_linear_variancia_zero():
    with pytest.raises(ZeroDivisionError):
        ajuste_linear([1, 1, 1], [2, 3, 4])


def test_ajuste_polinomial_tamanho_invalido():
    with pytest.raises(ValueError):
        ajuste_polinomial([1, 2], [4], n=2)


def test_ajuste_polinomial_poucos_pontos():
    with pytest.raises(ValueError):
        ajuste_polinomial([1], [5], n=1)


def test_ajuste_polinomial_grau_excede():
    with pytest.raises(ValueError):
        ajuste_polinomial([1, 2], [3, 4], n=2)
