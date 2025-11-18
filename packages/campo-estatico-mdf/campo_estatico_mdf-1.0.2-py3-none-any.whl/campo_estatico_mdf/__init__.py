"""
Paquete principal del proyecto *campo-estatico-mdf*.

Expone la clase pública:
    - LaplaceSolver2D

Esta clase implementa la solución numérica de la ecuación de Laplace 2D
usando métodos iterativos (Jacobi y Gauss–Seidel), con discretización MDF.
"""

from .solver import LaplaceSolver2D

__all__ = ["LaplaceSolver2D"]
