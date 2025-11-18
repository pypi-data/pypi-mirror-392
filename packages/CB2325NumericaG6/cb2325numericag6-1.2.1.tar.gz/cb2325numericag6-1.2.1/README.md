Esse projeto foi desenvolvido pelo Grupo 6 para a disciplina de Programação 2 (CB23) do IMPA Tech

Feito por:
<ul>
    <li>Arthur Barbosa Pinheiro</li>
    <li>Daniel Rodrigues Serqueira</li>
    <li>Gabriel Colatusso Castro Da Cruz</li>
    <li>Manuela Abati Bordeaux Ronconi</li>
    <li>Marcelo Miguel Alves Da Silva</li>
    <li>Mateus Almeida Oliveira</li>
    <li>Ryan Kevin Da Costa Felinto</li>
    <li>Sérgio Teixeira Rosa</li>
    <li>Thierry Ventura Marcolino Da Silva</li>
    <li>Vinícius Flesch Kern</li>
</ul>

<br/>

# Versão do projeto: v1.2.1

# Documentação

A biblioteca CB2325NumericaG6 é uma biblioteca de cálculo numérico para python que trabalha com funções de interpolação, aproximação, integração, busca de raízes, polinômios, etc.

## Instalação:
```shell
pip install CB2325NumericaG6
```

# Módulos:

- aproximacao
- core
- erros
- integracao
- interpolacao
- polinomios
- raizes

# Aproximação (.aproximacao)

Esse módulo é direcionado a funções de aproximação numérica.

## Funções:

`ajuste_linear(x, y)`:

[✅] Status: Concluído

```python
ajuste_linear(x: Sequence, y: Sequence) -> Polinomio
```
**Entrada:**

A função recebe duas listas de variáveis, uma de coordenadas X e outra de coordenadas Y correspondentes.

As listas devem ter tamanhos iguais, pois cada ponto Y corresponde ao respectivo ponto X.

**Retorno:**
A função retorna o ajuste linear $y = ax + b$ da série de pontos por meio de um `Polinomio` [a,b].

`ajuste_polinomial(x, y, n, precisao)`:

[✅] Status: Concluído

```python
ajuste_polinomial(x: Sequence, y: Sequence, n: int = 2, precisao: int = 5) -> Polinomio
```
**Entrada:**

A função recebe duas listas de variáveis, uma de coordenadas X e outra de coordenadas Y correspondentes e o inteiro n que diz o grau do polinomilo.
As listas devem ter tamanhos iguais, pois cada ponto Y corresponde ao respectivo ponto X.

**Retorno:**
A função retorna o ajuste polinomial $y = a_0*x^n + a_1*x^(n-1) + ... + a_n$ da série de pontos por meio de um `Polinomio`.

`plot_ajuste(x, y, ajustes, domain, num_points)`:

[✅] Status: Concluído

```python
plot_ajuste(
    x: Sequence, 
    y: Sequence, 
    ajustes: dict[str, Polinomio], 
    domain: Optional[Interval] = None,
    num_points: int = 100
) -> tuple[Figure, Axes]
```

**Descrição:**

Plota os dados originais (x, y) e um ou mais polinômios de ajuste.

**Entrada:**

  - `x` (Sequence): Lista de coordenadas X originais.
  - `y` (Sequence): Lista de coordenadas Y originais.
  - `ajustes` (dict[str, Polinomio]): Dicionário onde a chave é o rótulo (ex: "Linear") e o valor é o objeto Polinomio ajustado.
  - `domain` (Optional[Interval]): Intervalo [min, max] explícito para plotar.
  - `num_points` (int): Número de pontos para desenhar as curvas.

**Retorno:**

  - `tuple[plt.Figure, plt.Axes]`: Figura e eixos do gráfico plotado.

# Core (.core)

Esse módulo constitue classes genéricas para o funcionamento dos demais módulos.

## Classes:

`Domain` (Classe abstrata)

[✅] Status: Concluído

`Interval(Domain)`

[✅] Status: Concluído

**\_\_init\_\_(p1,p2)**: Cria um intervalo com ponto mínimo p1, e ponto máximo p2.

### Métodos mágicos:
- **\_\_contains\_\_**: Verifica se um intervalo está contido no outro, ou seja se [a,b] está contido [c,d].
- **\_\_str\_\_**
- **\_\_repr\_\_**

### Propriedades:
- **min**: Retorna o infimo do intervalo.
- **max**: Retorna o supremo do intervalo.
- **size**: Retorna o tamanho do intervalo.
- **half**: Retorna o ponto central do intervalo.

### Métodos:
- **copy()**: Retorna uma cópia do intervalo.
- **intersect(other: Interval) -> Optional[Interval]**: (⚠️ Use core.safe_intersect) Retorna a intersecção do intervalo com outro. Se a intersecção for nula, retorna None.

`RealFunction` (Classe abstrata)

[✅] Status: Concluído

### Atributos
- f: Callable[[float], float]: Função principal
- prime: Optional[Callable[[float], float]]: Derivada da função (Opcional)
- domain: Optional[Interval]: Domínio da função (Opcional)

### Métodos mágicos:
- **\_\_call\_\_(x)**: Calcula o valor da função no ponto x. 

### Métodos:
- **eval_safe(x)**: Calcula o valor da função no ponto x se estiver no dominio ou se ele for None.
- **prime_safe(x)**: Calcula o valor da derivada da função no ponto x se a derivada existir, e se estiver no dominio ou se o dominio for None.
- **plot(intervalo: Interval = None, pontos: int = 100) -> tuple(plt.Figure, plt.Axes)**: Retorna o plot da função

## Funções

`linspace(min, max, points)`

Cria uma lista com `points` pontos igualmente distribuídos por um intervalo [min,max].

[✅] Status: Concluído

```python
linspace(min: float, max: float, points: int) -> list[float]
```

**Entrada:**
- min (float): Valor mínimo do intervalo de pontos
- max (float): Vamor máximo do intervalo de pontos
- points (int): Quantidade de pontos

**Retorno:**
- list[float]: Lista de pontos igualmente distribuídos no intervalo

`safe_intersect(d1, d2)`

Faz a intersecção de dois intervalos, tratando o caso de um dos dois serem None.

[✅] Status: Concluído

```python
safe_intersect(d1: Optional['Interval'], d2: Optional['Interval']) -> Optional['Interval']
```

**Entrada:**
- d1 (Interval ou None)
- d2 (Interval ou None)

**Retorno:**
- Interval: Intersecção dos dois intervalos, ou se um deles ou a intersecção for None, retorna None.

# Erros (.erros)

Esse módulo é destinado ao cálculo de erros numéricos.

## Funções

`erro_absoluto(valor_real, valor_aproximado)`:

Calcula o erro absoluto entre um ou mais valores reais e aproximados.    
Esta função é 'vectorizada': ela aceita tanto números únicos
quanto arrays NumPy.

Fórmula: ea = |valor_real - valor_aprox|

[✅] Status: Concluído

```python
erro_absoluto(valor_real, valor_aprox)
```

**Entrada:**
- valor_real (float ou np.ndarray): O valor exato ou de referência.
- valor_aprox (float ou np.ndarray): O valor obtido ou medido.

**Retorno:**
- float ou np.ndarray: O erro absoluto.

`erro_relativo(valor_real, valor_aproximado)`:

Calcula o erro relativo entre um ou mais valores reais e aproximados.    
Esta função é 'vectorizada': ela aceita tanto números únicos
quanto arrays NumPy.

Fórmula: er = |valor_real - valor_aprox| / |valor_real|

[✅] Status: Concluído

```python
erro_relativo(valor_real, valor_aprox)
```

**Entrada:**
- valor_real (float ou np.ndarray): O valor exato ou de referência.
- valor_aprox (float ou np.ndarray): O valor obtido ou medido.

**Retorno:**
- float ou np.ndarray: O erro relativo.

[✅] Status: Concluído

# Integração (.integracao)

Módulo que compõe as funções de integração.

## Funções

`integral_trapezio(f, start, end, divisions)`

Esse método calcula a integral de uma função por aproximação trapezoidal.

[✅] Status: Concluído

```python
integral_trapezio(f:Callable, start: float, end: float, divisions: int) -> float
```

**Entrada:**
- f (Callable): Função a ser integrada
- start (float): Ponto inicial do intervalo
- end (float): Ponto final do intervalo
- divisions (int): Número de subdivisões do intervalo: números maiores implicam uma aproximação mais precisa, mas também consome mais CPU.

**Retorno:**
- float: Valor da integral.

`plot_integral_trapezio(f, start, end, divisions)`

Plota a função f e os trapézios de integração.

[✅] Status: Concluído

```python
plot_integral_trapezio(f: Callable, start: float, end: float, divisions: int) -> tuple[plt.Figure, plt.Axes]
```

**Retorno:**

- tuple[plt.Figure, plt.Axes]: Figura e eixos do gráfico plotado.

`integral_riemann(f, start, end, divisions)`

Este método calcula a integral de uma função por soma de Riemann (ponto médio).

[✅] Status: Concluído

```python
integral_riemann(f:Callable, start:float, end:float, divisions:int) -> float
```

**Entrada:**

- f (Callable): Função a ser integrada.
- start (float): Ponto inicial do intervalo.
- end (float): Ponto final do intervalo.
- divisions (int): Número de subdivisões do intervalo.

**Retorno:**

- float: Valor da integral.

`plot_integral_riemann(f, start, end, divisions)`

Plota a função f e os retângulos da soma de Riemann (ponto médio).

[✅] Status: Concluído

```python
plot_integral_riemann(f: Callable, start: float, end: float, divisions: int) -> tuple[plt.Figure, plt.Axes]
```

**Retorno:**

- tuple[plt.Figure, plt.Axes]: Figura e eixos do gráfico plotado.

# Interpolação (.interpolacao)

Módulo que compõe as funções de interpolação.

`Interpolator` é um `callable` que recebe `float` e retorna `float`

## Classes:

`HermiteInterpolation(RealFunction)`

[✅] Status: Concluído

**\_\_init\_\_(x, y, dy, domain: Optional[Interval])**: Cria uma interpolação polinomial de Hermite a partir da lista de pontos X, Y e derivadas DY.

### Atributos
- f: Callable[[float], float]: Função principal
- domain: Optional[Interval]: Domínio da função (Opcional)
- X: Sequence[float]: Lista de valores X
- Y: Sequence[float]: Lista de valores Y

### Métodos:

- **plot(...) -> tuple[Figure, Axes]**: Plota o gráfico do polinômio interpolador de Hermite.

`PolinomialInterpolation(RealFunction)`

[✅] Status: Concluído

**\_\_init\_\_(x, y, domain: Optional[Interval])**: Cria uma interpolação polinomial (Lagrange) a partir da lista de pontos X, Y.

### Atributos
- f: Callable[[float], float]: Função principal
- domain: Optional[Interval]: Domínio da função (Opcional)
- X: Sequence[float]: Lista de valores X
- Y: Sequence[float]: Lista de valores Y

### Métodos:

- **plot(...) -> tuple[Figure, Axes]**: Plota o gráfico do polinômio interpolador de Lagrange.

`PiecewiseLinearFunction(RealFunction)`

[✅] Status: Concluído

**\_\_init\_\_(X,Y, domain: Optional[Interval])**: Cria uma interpolação linear por partes a partir da lista de pontos X, Y

### Atributos
- f: Callable[[float], float]: Função principal
- domain: Optional[Interval]: Domínio da função (Opcional)
- X: Sequence[float]: Lista de valores X
- Y: Sequence[float]: Lista de valores Y

### Propriedades:
- **prime**: Retorna uma função da derivada da interpolação linear.

### Métodos:
- **evaluate(v: float) -> float**: Calcula o valor interpolado linearmente entre os pontos.
- **criar_segmento_polinomial(x1, x2, y1, y2) -> Polinomio**: Retorna um polinomio linear para os pontos dados.
- **encontrar_segmentos_raiz() -> List[Tuple[float,float]]**: Retorna uma lista com todos os intervalos [a,b] que contém raízes.
- **plot(...) -> tuple[Figure, Axes]**: Plota o gráfico da função linear por partes.

## Funções

`linear_interp(x, y)`

[✅] Status: Concluído

```python
linear_interp(x: Sequence, y: Sequence) -> PiecewiseLinearFunction
```

**Entrada:**

- x (Sequence): Lista de coordenadas do eixo X (estritamente crescente)
- y (Sequence): Lista de coordenadas do eixo Y

**Retorno:**
- PiecewiseLinearFunction: O objeto de interpolação linear por partes.

`poly_interp(x, y)`

[✅] Status: Concluído

```python
poly_interp(x: Sequence[float], y: Sequence[float]) -> PolinomialInterpolation
```

**Entrada:**

- x (Sequence): Lista de coordenadas do eixo X.
- y (Sequence): Lista de coordenadas do eixo Y.

**Retorno:**

- PolinomialInterpolation: Um objeto chamável que avalia o polinômio interpolador.

`hermite_interp(x, y, dy)`

[✅] Status: Concluído

```python
hermite_interp(x: Sequence[float], y: Sequence[float], dy: Sequence[float]) -> HermiteInterpolation
```

**Entrada:**

- x (Sequence): Lista de coordenadas do eixo X (estritamente crescente)
- y (Sequence): Lista de coordenadas do eixo Y
- dy (Sequence): Derivada dos valores para cada Y.

**Retorno:**
- HermiteInterpolation: Um objeto chamável que avalia o polinômio interpolador de Hermite.
# Polinomios (.polinomios)

Módulo para definição e cálculo de polinomios.

## Classes:

`Polinomio(RealFunction)`

Representa um polinômio como uma lista de coeficientes, ordenados do termo de **maior grau** para o termo constante.

[✅] Status: Concluído

### Métodos mágicos:
- **\_\_init\_\_(values: List[float], domain: Optional[Interval] = None)**
- **\_\_repr\_\_**
- **\_\_len\_\_**
- **\_\_getitem\_\_**
- **\_\_setitem\_\_**
- **\_\_mul\_\_, \_\_rmul\_\_** (por escalar)
- **\_\_neg\_\_**
- **\_\_add\_\_** (com outro Polinomio)
- **\_\_sub\_\_** (com outro Polinomio)
- **\_\_eq\_\_**

### Propriedades:
- **degree**: (int) Retorna o grau do polinômio
- **isZero**: (bool) Retorna True se o polinômio é nulo `[0.0]` ou False caso contrário.
- **prime**: (Callable[[float], float]) Retorna uma *função* (lambda) que avalia a derivada do polinômio em um ponto.

### Métodos:
- **evaluate(x: float) -> float**: Calcula o valor do polinômio em um determinado ponto.
- **dividir_por(divisor: Polinomio) -> Tuple[Polinomio, Polinomio]**: Realiza a divisão do polinomio por outro polinomio e retorna uma tupla da forma (Quociente, Resto).
- **get_limite_raizes() -> tuple[float, float]**: Calcula os limites inferior e superior no quais estão todas as raízes reais positivas do polinômio.
- **derivar() -> Polinomio**: Calcula a derivada do polinomio e retorna um novo objeto Polinomio correspondente.

## Funções

`lambdify(P)`

**Descrição:**

Cria e retorna uma função lambda (Callable) que avalia o polinômio P(x). É apenas um wrapper do método `evaluate` que pode ser passado para funções como `secante` ou `bisseccao`.

[✅] Status: Concluído

```python
lambdify(P: 'Polinomio') -> Callable[[float], float]:
```

**Entrada:**

- P (Polinomio): O objeto Polinomio a ser convertido.

**Retorno:**

- `Callable[[float], float]`: Uma função lambda que recebe x (float) e retorna P(x) (float).

# Raízes (.raizes)

Módulo com funções de busca de raíz e cálculo de número de raízes.


## Funções

`secante(f, a, b, tol)`, `bissecao(f, a, b, tol)`

[✅] Status: Concluído

```python
secante(f: Callable, a: float, b: float, tol: float = 1e-6) -> float
bissecao(f: Callable, a: float, b: float, tol: float = 1e-6) -> float
```

**Entrada:**
- f: Função a ser analizada
- a: Ponto inicial do intervalo da função f
- b: Ponto final do intervalo da função f
- tol: Tolerancia para o erro da aproximação final

**Retorno:**
- float: Aproximação da raiz da função.

`plot_secante(f, intervalo, a, b, tol)`, `plot_bisseccao(f, intervalo, a, b, tol)`

[✅] Status: Concluído

```python
plot_secante(f: Callable, intervalo:tuple[float, float], a: float, b: float, tol: float = 1e-6) -> Figure

plot_bisseccao(f: Callable, intervalo:tuple[float, float], a: float, b: float, tol: float = 1e-6) -> Figure
```

**Entrada:**
- f: Função a ser analizada
- intervalo: Intervalo de plotagem
- a: Ponto inicial da função f
- b: Ponto final da função f
- tol: Tolerancia para o erro da aproximação final

**Retorno:**
- fig: Imagem da plotagem gerada.

`newton_raphson(f, df, a, tol)`

[✅] Status: Concluído

```python
newton_raphson(f: Callable, df: Callable, a:float, tol: float = 1e-6)
```

**Entrada:**
- f: Função a ser analizada
- df: Derivada de f
- a: Ponto inicial da função f
- tol: Tolerancia para o erro da aproximação final

**Retorno:**
- float: Aproximação da raiz da função encontrada.

`plot_newton_raphson(f, intervalo, df, a, tol)`

[✅] Status: Concluído

```python
plot_newton_raphson(f: Callable, intervalo:tuple[float, float], df: Callable, a:float, tol: float = 1e-6) -> Figure
```

**Entrada:**
- f: Função a ser analizada
- intervalo: Intervalo de plotagem
- df: Primeira derivada de f
- a: Ponto inicial da função f
- tol: Tolerancia para o erro da aproximação final

**Retorno:**
- fig: Imagem da plotagem gerada.

`sturm(P, a, b)`

Calcula o número de raízes reais de um polinomio no intervalo (a,b].

[✅] Status: Concluído

```python
sturm(P: Polinomio, a: float, b: float) -> int
```

**Entrada:**

- P (Polinomio): Polinomio a ser avaliado.
- a (float): Extremo inferior do intervalo.
- b (float): Extremo superior do intervalo.

**Retorno:**
- int: Número de raízes reais no intervalo (a,b].
