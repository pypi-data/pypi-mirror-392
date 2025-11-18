=================
Tutorial de uso
=================

En esta sección se muestra cómo utilizar el paquete ``campo-estatico-mdf`` para
resolver la ecuación de Laplace en 2D, calcular el campo eléctrico y visualizar
los resultados.

Instalación
===========

Desde PyPI:

.. code-block:: bash

   pip install campo-estatico-mdf

Para un entorno de desarrollo local:

.. code-block:: bash

   pip install -e .

Imports básicos
===============

.. code-block:: python

   from campo_estatico_mdf import LaplaceSolver2D

   N = 51
   bc = {"left": 1.0, "right": 0.0, "top": 0.0, "bottom": 1.0}

   solver = LaplaceSolver2D(
       N=N,
       bc=bc,
       epsilon=1e-5,
       max_iter=50_000,
       method="jacobi",  # o "gauss_seidel"
   )

   V, n_iter, err = solver.solve()
   Ex, Ey = solver.compute_e_field(V)

   print(f"Iteraciones: {n_iter}, Error final: {err:.3e}")
   print("Forma de V:", V.shape)

Parámetros principales
======================

- ``N`` (*int*): número de puntos por lado de la malla (N×N).
- ``bc`` (*dict*): diccionario con condiciones de contorno Dirichlet:

  - ``"left"``, ``"right"``, ``"top"``, ``"bottom"`` (en Voltios).

- ``epsilon`` (*float*): tolerancia de convergencia. El criterio es::

    max|ΔV| < epsilon

- ``max_iter`` (*int*): máximo de iteraciones permitidas.
- ``method`` (*str*): método iterativo:

  - ``"jacobi"``: actualiza usando sólo la iteración anterior.
  - ``"gauss_seidel"`` o ``"gauss-seidel"``: actualiza in-place, reutilizando
    valores recién actualizados dentro de la misma iteración.

Valores devueltos por ``solve()``
=================================

.. code-block:: python

   V, n_iter, err = solver.solve()

- ``V`` (*np.ndarray*): matriz 2D (N×N) con el potencial electrostático.
- ``n_iter`` (*int*): número de iteraciones realizadas.
- ``err`` (*float*): valor de ``max|ΔV|`` en la última iteración.

Cálculo del campo eléctrico
===========================

Para obtener el campo eléctrico ``E = -∇V``:

.. code-block:: python

   Ex, Ey = solver.compute_e_field(V)

donde:

- ``Ex`` es la componente en x (``-∂V/∂x``).
- ``Ey`` es la componente en y (``-∂V/∂y``).

Uso con Streamlit (GUI)
=======================

El repositorio incluye una interfaz gráfica en Streamlit para experimentar con
el solver de forma interactiva.

Ejecutar la app localmente:

.. code-block:: bash

   # Activar entorno virtual (ejemplo en Windows con Git Bash)
   source .venv/Scripts/activate
   # Instalar dependencias
   pip install -r requirements.txt
   # Instalar el paquete en editable
   pip install -e .
   # Lanzar la app
   streamlit run app_streamlit/streamlit_app.py

Páginas de la app
-----------------

- **Simulación**: permite configurar N, ``epsilon``, ``max_iter``, método iterativo
  y contornos, mostrando:

  - Mapa de potencial ``V`` (heatmap).
  - Campo eléctrico ``E`` (gráfico quiver).
  - Métricas de convergencia: número de iteraciones, error final, tiempo, etc.

- **Documentación**: enlaza e incrusta la documentación generada con Sphinx 
  (GitHub Pages) dentro de la propia app mediante un iframe.
