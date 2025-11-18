# CB2325NumericaG6/test_raizes.py
import math
import pytest
import matplotlib
matplotlib.use("Agg") 
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from CB2325NumericaG6.raizes import (
    secante,
    bisseccao,            
    newton_raphson,
    plot_secante,
    plot_bisseccao,
    plot_newton_raphson,
    sturm,
)
from CB2325NumericaG6.polinomios import Polinomio

#funções base para testes 
f_sq2 = lambda x: x**2 - 2.0
df_sq2 = lambda x: 2.0 * x

f_cubic = lambda x: x**3 - x  
df_cubic = lambda x: 3.0 * x**2 - 1.0


# bissecção

def test_bisseccao_basico():
    r = bisseccao(f_sq2, 0.0, 2.0, tol=1e-10)
    assert r == pytest.approx(math.sqrt(2.0), rel=1e-8)

def test_bisseccao_sem_mudanca_de_sinal_gera_erro():
    g = lambda x: x**2 + 1.0  # > 0 em todo lugar
    with pytest.raises(ValueError):
        _ = bisseccao(g, -1.0, 2.0)

# secante

def test_secante_basico():
    r = secante(f_sq2, 1.0, 2.0, tol=1e-12)
    assert r == pytest.approx(math.sqrt(2.0), rel=1e-10)

def test_secante_div_zero_quando_f_constante():
    const = lambda x: 1.0
    with pytest.raises(ZeroDivisionError):
        _ = secante(const, 0.0, 1.0)


# Newton–Raphson

def test_newton_raphson_basico():
    r = newton_raphson(f_sq2, df_sq2, a=1.5, tol=1e-12)
    assert r == pytest.approx(math.sqrt(2.0), rel=1e-10)

def test_newton_raphson_df_zero_no_inicial():
    f = lambda x: x**3
    df = lambda x: 3.0 * x**2
    with pytest.raises(ZeroDivisionError):
        _ = newton_raphson(f, df, a=0.0, tol=1e-12)


def test_plot_bisseccao_retorna_figure(monkeypatch):
    monkeypatch.setattr(plt, "show", lambda: None)
    # escolher a,b com sinais opostos para f(x)=x^3-x
    fig = plot_bisseccao(f_cubic, (-2.0, 2.0), -1.5, -0.5, tol=1e-3)
    assert isinstance(fig, Figure)


def test_plot_secante_retorna_figure(monkeypatch):
    monkeypatch.setattr(plt, "show", lambda: None)
    fig = plot_secante(f_cubic, (-2.0, 2.0), -1.5, 0.5, tol=1e-3)
    assert isinstance(fig, Figure)

def test_plot_newton_raphson_retorna_figure(monkeypatch):
    monkeypatch.setattr(plt, "show", lambda: None)
    fig = plot_newton_raphson(f_cubic, (-2.0, 2.0), df_cubic, a=0.8, tol=1e-3)
    assert isinstance(fig, Figure)

def test_sturm_conta_raizes_corretamente():
    P = Polinomio([1.0, 1.0, -2.0])
    assert sturm(P, -3.0, 3.0) == 2
    assert sturm(P, -0.5, 0.5) == 0

def test_sturm_intervalo_invalido():
    P = Polinomio([1.0, 0.0, -1.0])  
    with pytest.raises(ValueError):
        _ = sturm(P, 1.0, 1.0)
    with pytest.raises(ValueError):
        _ = sturm(P, 2.0, -2.0)
