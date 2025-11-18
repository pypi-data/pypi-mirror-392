import matplotlib.pyplot as plt
import numpy as np
from typing import Callable
from numpy import linspace
# Falta implementar o linspace de core.py

def integral_trapezio(f:Callable, start: float, end: float, divisions: int) -> float:
    """Esse método calcula a integral de uma função por aproximação trapezoidal
    Args:
        f (Callable): Função a ser integrada
        start (float): Ponto inicial do intervalo
        end (float): Ponto final do intervalo
        divisions (int): Número de subdivisões do intervalo: números maiores implicam uma aproximação mais precisa, mas também consome mais CPU.
    Returns:
        float: Valor da integral.
    Examples:
        >>> import math
        >>> f = lambda x: math.sin(x)**2+math.cos(x)**2
        >>> i = integracao.integral(f, 0, 2, 1000)
        >>> print(i)
        2.0
    """
    
    sumVal: float = 0
    Xincrement: float = abs(start-end)/divisions
    
    i: float = start
    while i < end:
        area: float = ( f(i) + f(min(end, i+Xincrement)) )
        area *= Xincrement/2.0 if i+Xincrement < end else (end-i)/2.0
        
        sumVal += area
        i += Xincrement
    
    return sumVal

def plot_integral_trapezio(f: Callable, start: float, end: float, divisions: int) -> tuple[plt.Figure, plt.Axes]:
    """
    Plota a função f e os trapézios de integração (versão melhorada).
    """
    valor_integral = integral_trapezio(f, start, end, divisions)
    
    fig, ax = plt.subplots()
    
    # 1. Plota a curva suave da função
    x_func = np.linspace(start, end, 1000)
    # CORRIGIDO: Usa list comprehension para aplicar f
    y_func = [f(val) for val in x_func] 
    
    ax.plot(x_func, y_func, 'b-', label='f(x)')
    
    # 2. Gera os pontos para os nós dos trapézios
    x_div = np.linspace(start, end, divisions + 1)
    # CORRIGIDO: Usa list comprehension para aplicar f
    y_div = [f(val) for val in x_div]
    
    # 3. Desenha os trapézios (MELHORIA: usando fill_between)
    ax.fill_between(x_div, y_div, color='orange', alpha=0.4, label='Área do Trapézio')
    
    # 4. Plota os nós
    ax.plot(x_div, y_div, 'ro', markersize=4, label='Nós')
    
    ax.set_title(f"Integral (Trapézio): {valor_integral:.6f}")
    ax.grid(True)
    ax.legend()
    
    return fig, ax

def integral_riemann(f:Callable, start:float, end:float, divisions:int) -> float:
    """Este método calcula a integral de uma função por
    soma de Riemann
    Args:
        f (Callable): Função a ser integrada
        start (float): Ponto inicial do intervalo
        end (float): Ponto final do intervalo
        divisions (int): Número de subdivisões do intervalo: números maiores implicam uma aproximação mais precisa, mas também consome mais CPU.
    Returns:
        float: Valor da integral.
    Examples:
        >>> f = lambda x: x**2
        >>> i = integracao.integral_riemann(f, 0, 3, 1000)
        >>> print(round(i,2))
        9.0
    """
    base = abs(end - start)/divisions
    retangulos = [base * f(x) for x in linspace(start+base/2,end-base/2, divisions)]
    i = sum(retangulos)

    return i

def plot_integral_riemann(f: Callable, start: float, end: float, divisions: int) -> tuple[plt.Figure, plt.Axes]:
    """
    Plota a função f e os retângulos da soma de Riemann (ponto médio).
    """
    valor_integral = integral_riemann(f, start, end, divisions)
    fig, ax = plt.subplots()

    # 1. Plota a curva suave da função
    x_func = np.linspace(start, end, 1000)
    # CORRIGIDO: Usa list comprehension
    y_func = [f(val) for val in x_func]
    ax.plot(x_func, y_func, 'b-', label='f(x)')

    # 2. Prepara os dados para os retângulos
    base = (end - start) / divisions
    x_centers = np.linspace(start + base/2.0, end - base/2.0, divisions)
    # CORRIGIDO: Usa list comprehension
    y_heights = [f(val) for val in x_centers]

    # 3. Plota os retângulos usando ax.bar()
    ax.bar(x_centers, y_heights, width=base, 
           alpha=0.4, color='orange', edgecolor='black', 
           label='Retângulos (Riemann)')

    ax.set_title(f"Integral (Riemann - Ponto Médio): {valor_integral:.6f}")
    ax.grid(True)
    ax.legend()
    
    return fig, ax

if __name__ == "__main__":
    import math

    # --- Teste 1: Função Quadrática (poucas divisões) ---
    # f(x) = x^2. Integral de 0 a 3 é 9.
    
    f1 = lambda x: x**2
    
    print("Mostrando Teste 1: f(x) = x^2 (n=6)")
    # Usamos poucas divisões (6) para ver os trapézios claramente
    fig1, ax1 = plot_integral_trapezio(f1, start=0, end=3, divisions=6)
    plt.show()


    # --- Teste 2: Função Seno (usando math.sin) ---
    # f(x) = sin(x). Integral de 0 a pi é 2.
    
    # Esta função (math.sin) teria quebrado a versão original do plot
    f2 = lambda x: math.sin(x)
    
    print("Mostrando Teste 2: f(x) = sin(x) (n=10)")
    fig2, ax2 = plot_integral_trapezio(f2, start=0, end=math.pi, divisions=10)
    plt.show()


    # --- Teste 3: Polinômio Cúbico (muitas divisões) ---
    # f(x) = 0.1*x^3 - 0.5*x + 2
    
    f3 = lambda x: 0.1*x**3 - 0.5*x + 2
    
    print("Mostrando Teste 3: Polinômio Cúbico (n=50)")
    # Usamos muitas divisões (50) para mostrar a precisão
    fig3, ax3 = plot_integral_trapezio(f3, start=-3, end=4, divisions=50)
    plt.show()

    # --- Teste 1: Função Quadrática ---
    # f(x) = x^2 + 1.
    # Vamos usar poucas divisões (8) para ver os retângulos.
    
    f1 = lambda x: x**2 + 1
    
    print("Mostrando Teste 1: f(x) = x^2 + 1 (n=8)")
    fig1, ax1 = plot_integral_riemann(f1, start=-2, end=2, divisions=8)
    plt.show()


    # --- Teste 2: Função Seno (usando math.sin) ---
    # f(x) = sin(x) + 2.
    
    f2 = lambda x: math.sin(x) + 2
    
    print("Mostrando Teste 2: f(x) = sin(x) + 2 (n=12)")
    fig2, ax2 = plot_integral_riemann(f2, start=0, end=math.pi * 2, divisions=12)
    plt.show()