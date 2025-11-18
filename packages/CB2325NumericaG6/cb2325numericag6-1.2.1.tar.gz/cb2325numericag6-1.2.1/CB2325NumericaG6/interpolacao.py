from typing import Callable, Sequence, Optional, List, Tuple
from .core import RealFunction, Interval
from .polinomios import Polinomio
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import numpy as np

class HermiteInterpolation(RealFunction):
    def __init__(self, x: Sequence[float], y: Sequence[float], dy: Sequence[float], domain: Optional[Interval] = None):
        if len(x) != len(y) or len(x) != len(dy) or len(x) < 2:
            raise ValueError(f"x and y must have the same length ({len(x)} != {len(y)}) and have atleast 2 points.")
        self.X = x
        self.Y = y
        self.DY = dy
        self.domain = domain 
        self.f = self._coeficientes() # O Callable principal para RealFunction

    def _coeficientes(self):
        n = len(self.X)
        coef = [0.0 for _ in range(2*n)]

        for i in range(n):
            Li = [1.0]
            denom = 1.0
            for j in range(n):
                if j != i:
                    novo = [0.0 for _ in range(len(Li)+1)]
                    for k in range(len(Li)):
                        novo[k] -= Li[k] * self.X[j]
                        novo[k+1] += Li[k]
                    Li = novo
                    denom *= (self.X[i] - self.X[j])
            Li = [a / denom for a in Li]

            Li_prime = sum(1 / (self.X[i] - self.X[m]) for m in range(n) if m != i)

            Li2 = [0.0]*(2*len(Li)-1)
            for p in range(len(Li)):
                for q in range(len(Li)):
                    Li2[p+q] += Li[p]*Li[q]

            Ki = [0.0]*(len(Li2)+1)
            for k in range(len(Li2)):
                Ki[k] -= Li2[k] * self.X[i]
                Ki[k+1] += Li2[k]

            Hi = [0.0]*(len(Li2)+1)
            for k in range(len(Li2)):
                Hi[k] += Li2[k]
            for k in range(len(Li2)):
                Hi[k] += 2*Li_prime*Li2[k]*self.X[i]  
                Hi[k+1] -= 2*Li_prime*Li2[k]           
            termo = [0.0]*max(len(Hi), len(Ki))
            for k in range(len(Hi)):
                termo[k] += self.Y[i]*Hi[k]
            for k in range(len(Ki)):
                termo[k] += self.DY[i]*Ki[k]

            for k in range(len(termo)):
                coef[k] += termo[k]

        while len(coef) > 1 and abs(coef[-1]) < 1e-14:
            coef.pop()

        return Polinomio(coef[::-1])


    def plot(self, num_points: int = 100, margin: float = 0.2, domain: Optional[Interval] = None) -> tuple[Figure, Axes]: #type: ignore
            """
            Plota o gráfico do polinômio interpolador de Hermite.

            Args:
                num_points (int): Número de pontos para desenhar a curva do polinômio.
                margin (float): Percentual da margem a ser adicionada nos eixos x 
                                além dos pontos de dados min/max (usado apenas se domain=None).
                domain (Optional[Interval]): Intervalo [min, max] explícito para plotar. 
                                            Se None, usa o min/max dos pontos X com a margem.

            Returns:
                tuple[plt.Figure, plt.Axes]: Figura e eixos do gráfico plotado.
            Examples:
                
                >>> x_h1 = [0.0, 1.0, 2.0]
                >>> y_h1 = [1.0, 2.0, 0.0]
                >>> dy_h1 = [0.0, 1.0, -1.0]
                >>> P_h1 = hermite_interp(x_h1, y_h1, dy_h1)
                >>> fig_h1, ax_h1 = P_h1.plot()
                >>> plt.show()
            """
            fig, ax = plt.subplots()

            # --- Gera pontos para a curva ---
            if domain:
                # Usa o domínio explícito se fornecido
                plot_min = domain.min
                plot_max = domain.max
            else:
                # Lógica anterior: calcula o domínio baseado nos pontos e na margem
                x_min = min(self.X)
                x_max = max(self.X)
                span = x_max - x_min
                
                if span == 0: # Caso de emergência se os pontos forem idênticos
                    plot_min = x_min - 1.0
                    plot_max = x_max + 1.0
                else:
                    plot_min = x_min - span * margin
                    plot_max = x_max + span * margin

            X_plot = np.linspace(plot_min, plot_max, num_points)
            Y_plot = [self(x) for x in X_plot]

            # --- Plota ---
            # 1. A curva do polinômio
            ax.plot(X_plot, Y_plot, label="Interpolador Hermite", color="blue")
            
            # 2. Os pontos originais
            ax.scatter(self.X, self.Y, color="red", zorder=5, label="Pontos originais")

            # 3. As LINHAS das derivadas (em vez de setas)
            line_length = 0.3 # Comprimento total do segmento de reta
            segment_half_length = line_length / 2.0
            first_line = True
            
            for xi, yi, dyi in zip(self.X, self.Y, self.DY):
                label = "Derivadas" if first_line else None
                
                # Calcula o início e o fim do segmento de reta
                x1 = xi - segment_half_length
                y1 = yi - segment_half_length * dyi
                
                x2 = xi + segment_half_length
                y2 = yi + segment_half_length * dyi
                
                # Plota o segmento de reta
                ax.plot([x1, x2], [y1, y2], color='green', zorder=6, label=label)
                first_line = False

            # --- Configurações ---
            ax.set_title("Interpolação de Hermite")
            ax.set_xlabel("x")
            ax.set_ylabel("P(x)")
            ax.grid(True)
            ax.legend()
            
            return fig, ax

def hermite_interp(x: Sequence[float], y: Sequence[float], dy: Sequence[float], domain: Optional[Interval]=None) -> HermiteInterpolation:
    """
    Cria uma função de interpolação polinomial de Hermite a partir de um conjunto de coordenadas X, Y
    e de suas derivadas.

    Args:
        x (Sequence[float]): Coordenadas no eixo X.
        y (Sequence[float]): Valores de Y nas respectivas coordenadas.
        dy (Sequence[float]): Valores das derivadas nas respectivas coordenadas.
        domain (Optional[Interval]): domínio da função (opcional)
        
    Returns:
        HermiteInterpolation: Uma classe chamável que avalia o polinômio interpolador de Hermite.
        
    Raises:
        ValueError: Se x, y e dy tiverem comprimentos diferentes ou contiverem menos de dois pontos.
    """
    if len(x) != len(y) or len(x) != len(dy) or len(x) < 2:
        raise ValueError(
            f"x, y, dy must have the same length and contain at least two points "
        )

    return HermiteInterpolation(x, y, dy, domain)
 


class PolinomialInterpolation(RealFunction):
    def __init__(self, x: Sequence[float], y: Sequence[float], domain: Optional[Interval] = None):
        if len(x) != len(y) or len(x) < 2:
            raise ValueError(f"x and y must have the same length ({len(x)} != {len(y)}) and have atleast 2 points.")
        self.X = x
        self.Y = y
        self.domain = domain
        self.f = self._coeficientes() # O Callable principal para RealFunction

    def _coeficientes(self) -> Polinomio:
        n = len(self.X)
        coef = [0.0 for _ in range(n)]

        for i in range(n): 
            Li = [1.0]
            denom = 1.0

            for j in range(n): 
                if i != j:
                    novo = [0.0 for _ in range(len(Li) + 1)]
                    for k in range(len(Li)):
                        novo[k]     += Li[k]          
                        novo[k + 1] -= Li[k] * self.X[j]
                    Li = novo
                    denom *= (self.X[i] - self.X[j])

            Li = [a * (self.Y[i] / denom) for a in Li]
            for k in range(len(Li)):
                coef[k] += Li[k]

        return Polinomio(coef) 

    def plot(self, num_points: int = 100, margin: float = 0.2, domain: Optional[Interval] = None) -> tuple[Figure, Axes]: #type: ignore
        """
        Plota o gráfico do polinômio interpolador de Lagrange.

        Args:
            num_points (int): Número de pontos para desenhar a curva do polinômio.
            margin (float): Percentual da margem (usado se domain=None).
            domain (Optional[Interval]): Intervalo [min, max] explícito para plotar.

        Returns:
            tuple[plt.Figure, plt.Axes]: Figura e eixos do gráfico plotado.
        Examples:
                >>> x_poly = [0, 1, 2, 3]
                >>> y_poly = [1, 2, 0, 5]
                >>> P_poly = poly_interp(x_poly, y_poly)
                >>> fig_poly, ax_poly = P_poly.plot() 
                >>> plt.show()
        """
        fig, ax = plt.subplots()

        # --- Gera pontos para a curva ---
        if domain:
            # Usa o domínio explícito se fornecido
            plot_min = domain.min
            plot_max = domain.max
        else:
            # Calcula o domínio baseado nos pontos e na margem
            x_min = min(self.X)
            x_max = max(self.X)
            span = x_max - x_min
            
            if span == 0: 
                plot_min = x_min - 1.0
                plot_max = x_max + 1.0
            else:
                plot_min = x_min - span * margin
                plot_max = x_max + span * margin

        X_plot = np.linspace(plot_min, plot_max, num_points)
        Y_plot = [self(x) for x in X_plot]

        # --- Plota ---
        # 1. A curva do polinômio
        ax.plot(X_plot, Y_plot, label="Interpolador Polinomial", color="blue")
        
        # 2. Os pontos originais
        ax.scatter(self.X, self.Y, color="red", zorder=5, label="Pontos originais")

        # --- Configurações ---
        ax.set_title("Interpolação Polinomial")
        ax.set_xlabel("x")
        ax.set_ylabel("P(x)")
        ax.grid(True)
        ax.legend()
        
        return fig, ax
    
    

 
def poly_interp(x: Sequence[float], y: Sequence[float], domain: Optional[Interval] = None) -> PolinomialInterpolation:
    """
    Cria uma função de interpolação polinomial a partir de um conjunto de coordenadas X e Y,
    utilizando a forma de Lagrange.

    Args:
        x (Sequence[float]): Sequência das coordenadas no eixo X.
        y (Sequence[float]): Sequência dos valores correspondentes no eixo Y.
        domain (Optional[Interval]): domínio da função (opcional)

    Returns:
        PolinomialInterpolation: Uma classe chamável que avalia o polinômio interpolador
        para qualquer valor de entrada do tipo float.

    Raises:
        ValueError: Se x e y tiverem comprimentos diferentes ou contiverem menos de dois pontos.
    """
    if len(x) != len(y) or len(x) < 2:
        raise ValueError(f"x and y must have the same length ({len(x)} != {len(y)}) and have atleast 2 points.")
    
    return PolinomialInterpolation(x, y, domain)




class PiecewiseLinearFunction(RealFunction):
    def __init__(self, x: Sequence[float], y: Sequence[float], domain: Optional[Interval] = None):
        self.X = x
        self.Y = y
        self.domain = domain if domain else Interval(min(x), max(x))
        self.f = self.evaluate # O Callable principal para RealFunction

    def criar_segmento_polinomial(self, x1, x2, y1, y2) -> Polinomio:
        if x1 == x2:
            raise ValueError("Pontos x1 e x2 são o mesmo. Não é possível criar um segmento.")

        slope = (y2-y1)/(x2-x1)
        c0 = y1 - slope * x1
        segmentDomain = Interval(min(x1, x2), max(x1, x2))

        pol = Polinomio([slope, c0], segmentDomain) 

        return pol

    @property
    def prime(self) -> Callable[[float], float]: #type: ignore
        """
        Retorna a função que calcula a derivada (inclinação constante) 
        da interpolação linear por partes. A derivada é indefinida nos pontos de referência.
        """
        
        # O self.prime da RealFunction é um Callable. Retornamos uma função que implementa a lógica da derivada.
        def piecewisePrimeFunction(v: float) -> float:
            if not (self.X[0] <= v <= self.X[-1]):
                raise ValueError(f"O ponto {v} está fora do domínio de interpolação.")
            
            n = len(self.X)
            
            for x_i in self.X:
                if abs(v - x_i) < 1e-12: 
                    raise ValueError(f"A derivada é descontínua e indefinida no nó x={v}.")

            start, end = 0, n - 1

            while end - start != 1:
                mid = (end + start) // 2
                if self.X[mid] > v:
                    end = mid
                else:
                    start = mid
            
            x1, x2 = self.X[start], self.X[end]
            y1, y2 = self.Y[start], self.Y[end]
            
            slope = (y2 - y1) / (x2 - x1)
            
            return slope

        return piecewisePrimeFunction

    def evaluate(self, v: float) -> float:
        n = len(self.X)
        if v > self.X[-1]:
            start, end = n - 2, n - 1
        elif v < self.X[0]:
            start, end = 0, 1
        elif v == self.X[0]:
            return self.Y[0]
        elif v == self.X[-1]:
            return self.Y[-1]
        else:
            start, end = 0, n - 1 
            while end - start != 1:
                mid = (end + start) // 2
                if self.X[mid] > v:
                    end = mid
                elif self.X[mid] < v:
                    start = mid
                else:
                    return self.Y[mid] 

        x1, x2 = self.X[start], self.X[end]
        y1, y2 = self.Y[start], self.Y[end]

        return y1 + (v - x1) * ((y2 - y1) / (x2 - x1))
    
    def encontrar_segmentos_raiz(self) -> List[Tuple[float, float]]:
        """
        Retorna uma lista de intervalos [a, b] onde f(a) * f(b) < 0.
        """

        segments = []
        for i in range(len(self.X) - 1):
            y_i = self.Y[i]
            y_i_plus_1 = self.Y[i+1]
            
            # Se os sinais são opostos (garantia da raiz)
            if y_i * y_i_plus_1 < 0:
                segments.append((self.X[i], self.X[i+1]))
                
            if y_i == 0:
                segments.append((self.X[i], self.X[i]))

        if self.Y[-1] == 0:
            segments.append((self.X[-1], self.X[-1]))
            
        return segments
    
    def plot(self, *args, **kwargs) -> tuple[Figure, Axes]:
        """
        Plota o gráfico da função linear por partes.
        Returns:
            tuple[plt.Figure, plt.Axes]: Figura e eixos do gráfico plotado.
        Examples:
            >>> x = [0, 2, 4, 5]
            >>> y = [1, 2, 0, 4]
            >>> p = linear_interp(x, y)
            >>> fig, ax = p.plot()
            >>> plt.show()
        """
        fig, ax = plt.subplots()
        # Plota as linhas que interligam os pontos
        ax.plot(self.X, self.Y, linestyle='-', color='blue', label='Função Linear por Partes')

        # Plota os pontos de dados individuais
        ax.plot(self.X, self.Y, 'o', color='red', label='Pontos de Dados') # 'o' para marcadores de círculo

        ax.set_title("Gráfico da Função Linear por Partes")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.grid(True)
        ax.legend() # Mostra a legenda dos elementos plotados

        return fig, ax
        
    
def linear_interp(x: Sequence, y: Sequence) -> PiecewiseLinearFunction:
    """Cria uma função de interpolação (e extrapolação)s linear a partir de um par de sequências de coordenadas X,Y
    assumindo que os valores X são estritamente crescentes.

    Args:
        x (Sequence): Lista de coordenadas do eixo X (estritamente crescente)
        y (Sequence): Lista de coordenadas do eixo Y
    
    Returns:
        Interpolator: Uma função que retorna o valor interpolado linearmente baseado nos valores X, Y.
    Raises:
        ValueError: Se a quantidade de elementos de X e Y forem diferentes ou tiverem menos de dois pontos.
    Examples:
        >>> x = [0, 2, 4, 5]
        >>> y = [1, 2, 0, 4]
        >>> p = linear_interp(x, y)
        >>> print(p(1.5))
        1.75
    """
    
    if len(x) != len(y):
        raise ValueError("Lenght of X is different of Y")
    if len(x) < 2:
        raise ValueError("There must be atleast 2 points")
    
    return PiecewiseLinearFunction(x, y)


if __name__ == "__main__":

# --- Teste da linear_interp ---
    x = [0, 1, 2, 3, 4]
    y = [1, 3, 2, 5, 4]
    plf = linear_interp(x, y)
    fig, ax = plf.plot()
    plt.show()

    a = [-1, 0, 1, 2]
    b = [1, -2, 0, 2]
    plf2 = linear_interp(a, b)  
    fig2, ax2 = plf2.plot()
    plt.show()

    # --- Teste da poly_interp ---
    x_poly = [0, 1, 2, 3]
    y_poly = [1, 2, 0, 5]

    # Usando a função poly_interp
    P_poly = poly_interp(x_poly, y_poly)
    fig_poly, ax_poly = P_poly.plot(domain=Interval(0, 3.0), num_points=31) 
    ax_poly.set_title("Interpolação Polinomial")
    plt.show()

# --- Teste 1: Exemplo simples ---
    x_h1 = [0.0, 1.0, 2.0]
    y_h1 = [1.0, 2.0, 0.0]
    dy_h1 = [0.0, 1.0, -1.0]

    P_h1 = hermite_interp(x_h1, y_h1, dy_h1)
    fig_h1, ax_h1 = P_h1.plot()
    plt.show()

# --- Teste para o caso de 4 pontos (usando o método .plot) ---
    x_h3 = [0.0, 1.0, 2.0, 3.0]
    y_h3 = [1.0, 2.0, 4.5, 2.5]
    dy_h3 = [0.0, 1.0, -0.5, 0.5]

    # --- Cria interpolador de Hermite ---
    P_h3 = hermite_interp(x_h3, y_h3, dy_h3)
    fig_h3, ax_h3 = P_h3.plot()
    ax_h3.set_title("Interpolação de Hermite com 4 pontos")
    plt.show()