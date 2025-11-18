import math
import statistics
from .core import Interval
from .polinomios import Polinomio
from typing import Optional, Sequence
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import numpy as np

def ajuste_linear(x: Sequence, y: Sequence) -> Polinomio:
    """
    Ajusta y = a*x + b aos pontos (x, y) por mínimos quadrados (erro vertical).

    Args:
        x: Valores da variável independente.
        y: Valores da variável dependente (mesmo tamanho de x).

    Returns:
        Polinomio: Classe Polinomio contendo os coeficientes

    Raises:
        ValueError: Tamanhos diferentes ou menos de dois pontos.
        ZeroDivisionError: Variância de x igual a zero.
    """
    n = len(x)
    if n != len(y):
        raise ValueError("Ambas as listas devem ter o mesmo tamanho.")
    if n < 2:
        raise ValueError("Precisa de pelo menos dois pontos.")

    mx = statistics.mean(x)
    my = statistics.mean(y)

    cov_xy = math.fsum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    var_x  = math.fsum((xi - mx) ** 2 for xi in x)

    if var_x == 0.0:
        raise ZeroDivisionError("A variância de x é zero.")

    a = cov_xy / var_x
    b = my - a * mx
    return Polinomio([a,b])

def ajuste_polinomial(x: Sequence, y: Sequence, n = 2, precisao = 5) -> Polinomio:
    """
    Ajusta y = a_0*x^n + a_1*x^(n-1) + ... + a_n aos pontos (x,y) por mínimos quadrados (erro vertical)

    Args:
        x: Valores da variável independente.
        y: Valores da variável dependente (mesmo tamanho de x).

    Returns:
        Polinomio: Classe Polinomio contendo os coeficientes

    Raises:
        ValueError: Tamanhos diferentes, menos de dois pontos ou grau inadequado.
        ZeroDivisionError: Variância de x igual a zero.
    """

    if len(x) != len(y):
        raise ValueError("Ambas as listas devem ter o mesmo tamanho.")
    if len(x) < 2:
        raise ValueError("Precisa de pelo menos dois pontos.")
    if n > len(x) - 1:
        raise ValueError("O grau do polinomio deve ser menor que o numero de pontos.")
    X = np.array(x)
    Y = np.array(y)
    Coeficientes = np.polyfit(X,Y,n)
    Poly = Polinomio([round(Coeficientes[i],precisao) for i in range(len(Coeficientes))])
    return Poly

def plot_ajuste(x: Sequence, y: Sequence, ajustes: dict[str, Polinomio], domain: Optional[Interval] = None,num_points: int = 100) -> tuple[Figure, Axes]:
    """
    Plota os dados originais (x, y) e um ou mais polinômios de ajuste.

    Args:
        x (list[float]): Lista de coordenadas X originais.
        y (list[float]): Lista de coordenadas Y originais.
        ajustes (dict[str, Polinomio]): Dicionário onde a chave é o rótulo
                                        (ex: "Linear") e o valor é o 
                                        objeto Polinomio ajustado.
        domain (Optional[Interval]): Intervalo [min, max] explícito para plotar.
                                     Se None, usa o min/max dos pontos X com margem.
        num_points (int): Número de pontos para desenhar as curvas.

    Returns:
        tuple[plt.Figure, plt.Axes]: Figura e eixos do gráfico plotado.
    """
    fig, ax = plt.subplots()

    # 1. Plota os pontos de dados originais
    ax.scatter(x, y, color='red', zorder=5, label="Pontos Originais")

    # 2. Determina o domínio de plotagem
    if domain:
        plot_min = domain.min
        plot_max = domain.max
    else:
        # Lógica para calcular o domínio com margem
        x_min, x_max = min(x), max(x)
        span = x_max - x_min
        margin = 0.1 # Margem pequena para ajustes
        if span == 0:
            plot_min, plot_max = x_min - 0.5, x_max + 0.5
        else:
            plot_min = x_min - span * margin
            plot_max = x_max + span * margin
    
    # 3. Gera os pontos da(s) curva(s) de ajuste
    X_plot = np.linspace(plot_min, plot_max, num_points)
    
    # 4. Plota cada polinômio de ajuste
    for label, polinomio in ajustes.items():
        # Assegura que o Polinomio é 'callable' (via RealFunction)
        Y_plot = [polinomio(val) for val in X_plot]
        ax.plot(X_plot, Y_plot, label=label)

    # 5. Configurações do gráfico
    ax.set_title("Ajuste de Mínimos Quadrados")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True)
    ax.legend()
    
    return fig, ax

if __name__ == "__main__":
    x = [0, 1, 2, 3, 4]
    y = [1.1, 1.9, 3.0, 3.9, 5.2]

    # 1. Calcula os ajustes
    Px = ajuste_linear(x,y)
    Px_2 = ajuste_polinomial(x,y,2)
    Px_3 = ajuste_polinomial(x,y,3)

    # 2. Imprime os resultados
    print("Ajuste Linear: ", f"y = {Px[0]:.2f}x + {Px[1]:.2f}")
    print("Ajuste quadrático:",f"y = {Px_2[0]:.2f}x^2 + {Px_2[1]:.2f}x + {Px_2[2]:.2f}")
    print("Ajuste cúbico:",f"y = {Px_3[0]:.2f}x^3 + {Px_3[1]:.2f}x^2 + {Px_3[2]:.2f}x + {Px_3[3]:.2f}")

    # 3. Plota os ajustes usando a nova função
    
    # Exemplo 1: Plotando todos os ajustes juntos
    ajustes_todos = {
        "Linear": Px,
        "Quadrático": Px_2,
        "Cúbico": Px_3
    }
    fig1, ax1 = plot_ajuste(x, y, ajustes_todos)
    ax1.set_title("Comparação de Ajustes")
    plt.show()

    # Exemplo 2: Plotando apenas o ajuste linear
    ajuste_linear_apenas = {
        "Linear": Px
    }
    fig2, ax2 = plot_ajuste(x, y, ajuste_linear_apenas)
    ax2.set_title("Apenas Ajuste Linear")
    plt.show()