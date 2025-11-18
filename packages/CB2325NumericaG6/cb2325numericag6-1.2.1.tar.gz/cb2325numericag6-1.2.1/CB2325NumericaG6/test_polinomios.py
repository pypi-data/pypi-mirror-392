import math
import pytest

from CB2325NumericaG6.polinomios import Polinomio, lambdify
from CB2325NumericaG6.core import Interval

# ----------------------
# construção/representação
# ----------------------
def test_repr_len_degree_iszero_evaluate_horner():
    P = Polinomio([3.0, 2.0, -1.0])  # 3x^2 + 2x - 1
    assert len(P) == 3
    assert P.degree == 2
    assert not P.isZero
    # Horner em x=2: 3*4 + 2*2 - 1 = 12 + 4 - 1 = 15
    assert P.evaluate(2.0) == pytest.approx(15.0, rel=1e-12)


def test_limpa_coeficientes_lideres_muito_pequenos():
    # primeiro coeficiente é menor que a tolerância relativa => vira 0 e é removido
    Q = Polinomio([1e-20, 2.0, 3.0])  # vira 2x + 3
    assert Q.degree == 1
    assert Q.evaluate(10.0) == pytest.approx(23.0, rel=1e-12)


# ----------------------
# indexadores
# ----------------------
def test_get_set_item_e_indices_negativos():
    P = Polinomio([3.0, 2.0, -1.0])
    assert P[0] == 3.0
    assert P[-1] == -1.0
    P[1] = 5.0
    assert P[1] == 5.0
    with pytest.raises(IndexError):
        _ = P[10]
    with pytest.raises(IndexError):
        P[10] = 0.0


# ----------------------
# operações básicas
# ----------------------
def test_neg_mul_add_sub():
    P = Polinomio([1.0, 2.0, 3.0])     # x^2 + 2x + 3
    Q = Polinomio([2.0, -1.0, 4.0])    # 2x^2 - x + 4

    # -P
    assert (-P).evaluate(2.0) == pytest.approx(-(P.evaluate(2.0)), rel=1e-12)

    # c*P
    R = 2 * P
    assert R.evaluate(3.0) == pytest.approx(2 * P.evaluate(3.0), rel=1e-12)

    # P+Q e P-Q
    S = P + Q  # (1+2)x^2 + (2-1)x + (3+4) = 3x^2 + x + 7
    T = P - Q  # (1-2)x^2 + (2-(-1))x + (3-4) = -x^2 + 3x - 1
    assert S.evaluate(2.0) == pytest.approx(3*(2**2) + 1*2 + 7, rel=1e-12)
    assert T.evaluate(2.0) == pytest.approx(-(2**2) + 3*2 - 1, rel=1e-12)


def test_soma_preserva_intersecao_de_dominios():
    P = Polinomio([1.0, 0.0], Interval(0.0, 1.0))      # domínio [0,1]
    Q = Polinomio([1.0, 1.0], Interval(0.5, 2.0))       # domínio [0.5,2]
    S = P + Q
    assert isinstance(S.domain, Interval)
    # Interseção esperada: [0.5, 1.0]
    assert 0.5 in S.domain
    assert 1.0 in S.domain
    assert 0.49 not in S.domain
    assert 1.01 not in S.domain

# ----------------------
# derivada e prime
# ----------------------
def test_derivar_e_prime_property():
    P = Polinomio([3.0, 2.0, -1.0])    # 3x^2+2x-1  ->  6x+2
    dP = P.derivar()
    assert isinstance(dP, Polinomio)
    # prime usa derivar internamente
    x = 5.0
    assert P.prime(x) == pytest.approx(dP.evaluate(x), rel=1e-12)
    assert dP._values == [6.0, 2.0]


# ----------------------
# divisão polinomial
# ----------------------
def test_divide_by_constante():
    P = Polinomio([4.0, 6.0, 8.0])   # 4x^2+6x+8
    D = Polinomio([2.0])             # 2
    Q, R = P.dividir_por(D)
    # (4x^2+6x+8)/2 = 2x^2+3x+4, resto 0
    assert Q._values == [2.0, 3.0, 4.0]
    assert R._values == [0.0]


def test_divide_by_mesmo_grau_da_docstring():
    p1 = Polinomio([4.0, 6.0, 8.0])
    p2 = Polinomio([2.0, 3.0, 4.0])
    Q, R = p1.dividir_por(p2)
    assert Q._values == [2.0]
    assert R._values == [0.0]


def test_divide_by_zero_gera_erro():
    with pytest.raises(ValueError):
        _ = Polinomio([1.0]).dividir_por(Polinomio([0.0]))


# ----------------------
# limites para raízes reais (Cauchy)
# ----------------------
def test_get_real_root_bounds_cobre_raizes_reais():
    # (x-1)(x+2) = x^2 + x - 2  -> raízes reais -2 e 1
    P = Polinomio([1.0, 1.0, -2.0])
    l, L = P.get_limite_raizes()
    assert l <= -2.0 + 1e-12   # bound inferior cobre -2
    assert L >= 1.0 - 1e-12    # bound superior cobre 1


# ----------------------
# lambdify
# ----------------------
def test_lambdify_equivale_a_evaluate():
    P = Polinomio([2.0, 0.0, -3.0])  # 2x^2 - 3
    f = lambdify(P)
    for x in [-2.5, -1.0, 0.0, 3.3]:
        assert f(x) == pytest.approx(P.evaluate(x), rel=1e-12)


# ----------------------
# domínio propagado por interseção
# ----------------------
def test_operacoes_preservam_domain_por_intersecao():
    P = Polinomio([1.0, 0.0], Interval(-1.0, 2.0))
    Q = Polinomio([1.0, -1.0], Interval(1.0, 3.0))
    R = P - Q
    assert isinstance(R.domain, Interval)
    # Interseção esperada: [1.0, 2.0]
    assert 1.0 in R.domain
    assert 2.0 in R.domain
    assert 0.99 not in R.domain
    assert 2.01 not in R.domain