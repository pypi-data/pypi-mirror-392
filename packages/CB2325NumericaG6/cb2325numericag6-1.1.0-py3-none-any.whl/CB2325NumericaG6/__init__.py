# Módulos principais (classes base e utilidades)
from .core import (
    Domain,
    Interval,
    RealFunction,
    linspace,
    safe_intersect
)

# Polinômios
from .polinomios import (
    Polinomio,
    lambdify
)

# Interpolação (Classes de Interpolação e Funções de Fábrica)
from .interpolacao import (
    HermiteInterpolation,
    PolinomialInterpolation,
    PiecewiseLinearFunction,
    hermite_interp,
    poly_interp,
    linear_interp
)

# Aproximação e Ajuste
from .aproximacao import (
    ajuste_linear,
    ajuste_polinomial
)

# Raízes
from .raizes import (
    secante,
    plot_secante,
    bisseccao,
    plot_bisseccao,
    newton_raphson,
    plot_newton_raphson,
    sturm
)

# Erros
from .erros import (
    erro_absoluto,
    erro_relativo
)

# Integração
from .integracao import (
    integral_trapezio,
    plot_integral_trapezio,
    integral_riemann,
    plot_integral_riemann
)


# Define o que será exportado quando um usuário fizer 'from CB2325NumericaG6 import *'
__all__ = [
    # Core
    'Domain',
    'Interval',
    'RealFunction',
    'linspace',
    'safe_intersect',
    
    # Polinômios
    'Polinomio',
    'lambdify',
    
    # Interpolação
    'HermiteInterpolation',
    'PolinomialInterpolation',
    'PiecewiseLinearFunction',
    'hermite_interp',
    'poly_interp',
    'linear_interp',
    
    # Aproximação
    'ajuste_linear',
    'ajuste_polinomial',
    
    # Raízes
    'secante',
    'plot_secante',
    'bisseccao',
    'plot_bisseccao',
    'newton_raphson',
    'plot_newton_raphson',
    'sturm',
    
    # Erros
    'erro_absoluto',
    'erro_relativo',
    
    # Integração
    'integral_trapezio',
    'plot_integral_trapezio',
    'integral_riemann',
    'plot_integral_riemann'
]