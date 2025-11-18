import math
import pytest

from CB2325NumericaG6.integracao import integral_trapezio, integral_riemann

# 1) Constante — trapézio é exato
def test_integral_trapezio_constante_exato():
    f = lambda x: 3.5
    assert integral_trapezio(f, 2.0, 5.0, 10) == pytest.approx(3.5 * (5.0 - 2.0), rel=1e-12)

# 2) Linear — trapézio é exato
def test_integral_trapezio_linear_exato():
    f = lambda x: x
    assert integral_trapezio(f, 0.0, 1.0, 100) == pytest.approx(0.5, rel=1e-12)

# 3) Quadrática
@pytest.mark.parametrize("n, tol", [(10, 5e-3), (100, 5e-4), (1000, 5e-5)])
def test_integral_trapezio_quadratica_converge(n, tol):
    f = lambda x: x * x          # integral_trapezio de 0 a 1 é 1/3
    val = integral_trapezio(f, 0.0, 1.0, n)
    assert val == pytest.approx(1.0 / 3.0, abs=tol)

# 4) Identidade trigonométrica(1 = sen^2 + cos^2)
def test_integral_trapezio_trig_identidade():
    f = lambda x: math.sin(x)**2 + math.cos(x)**2
    assert integral_trapezio(f, 0.0, 2.0, 1000) == pytest.approx(2.0, rel=1e-10)

# 5) Intervalo degenerado
def test_integral_trapezio_intervalo_vazio():
    f = lambda x: x**2
    assert integral_trapezio(f, 1.234, 1.234, 50) == pytest.approx(0.0, abs=1e-15)

# 6) Divisions inválido
@pytest.mark.parametrize("n", [0])
def test_integral_trapezio_divisions_invalido(n):
    f = lambda x: x
    with pytest.raises((ZeroDivisionError, ValueError)):
        integral_trapezio(f, 0.0, 1.0, n)

# Testes para integral_riemann
# 1) Constante — regra do ponto médio é exata
def test_integral_riemann_constante_exato():
    f = lambda x: 3.5
    val = integral_riemann(f, 2.0, 5.0, 10)
    esperado = 3.5 * (5.0 - 2.0)
    assert val == pytest.approx(esperado, rel=1e-12)

# 2) Linear — regra do ponto médio também é exata
def test_integral_riemann_linear_exato():
    f = lambda x: x        # integral de 0 a 1 é 1/2
    val = integral_riemann(f, 0.0, 1.0, 7)   # qualquer n > 0 serve
    assert val == pytest.approx(0.5, rel=1e-12)

# 3) Quadrática — testar convergência com n crescente
@pytest.mark.parametrize("n, tol", [(10, 5e-3), (100, 5e-5), (1000, 5e-7)])
def test_integral_riemann_quadratica_converge(n, tol):
    f = lambda x: x * x    # integral de 0 a 1 é 1/3
    val = integral_riemann(f, 0.0, 1.0, n)
    assert val == pytest.approx(1.0 / 3.0, abs=tol)

# 4) Identidade trigonométrica — função constante 1, deve ser exata
def test_integral_riemann_trig_identidade():
    f = lambda x: math.sin(x)**2 + math.cos(x)**2  # ≡ 1
    val = integral_riemann(f, 0.0, 2.0, 1000)     # integral de 0 a 2 é 2
    assert val == pytest.approx(2.0, rel=1e-12)

# 5) Intervalo degenerado — a = b, integral deve ser zero
def test_integral_riemann_intervalo_vazio():
    f = lambda x: x**2
    val = integral_riemann(f, 1.234, 1.234, 50)
    assert val == pytest.approx(0.0, abs=1e-15)

# 6) Divisions inválido — n = 0 deve levantar erro
@pytest.mark.parametrize("n", [0])
def test_integral_riemann_divisions_invalido(n):
    f = lambda x: x
    with pytest.raises((ZeroDivisionError, ValueError)):
        integral_riemann(f, 0.0, 1.0, n)
