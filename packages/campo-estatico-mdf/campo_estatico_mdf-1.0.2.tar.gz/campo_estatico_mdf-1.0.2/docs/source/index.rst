====================================================
Documentación del proyecto *campo-estatico-mdf*
====================================================

Este sitio contiene la documentación oficial del paquete **campo-estatico-mdf**, 
que resuelve la ecuación de Laplace en 2D mediante diferencias finitas (MDF) 
y métodos iterativos (Jacobi y Gauss–Seidel). Incluye también el cálculo del 
campo eléctrico y una interfaz gráfica en Streamlit.

Contenido
=========

.. toctree::
   :maxdepth: 2

   teoria
   tutorial
   api_reference

Novedades recientes
===================

Versión 1.0.2 — Corrección del método Gauss–Seidel
---------------------------------------------------

En esta versión se corrigió un error donde el método **Gauss–Seidel** ejecutaba 
solo una iteración sin actualizar correctamente el potencial.  
Ahora:

- Itera in-place correctamente.
- El criterio de convergencia ``max|ΔV| < epsilon`` funciona como debía.
- Las soluciones convergen de forma comparable a Jacobi.
- Se añadieron pruebas unitarias de regresión para garantizar estabilidad.

Instalación
===========

.. code-block:: bash

   pip install campo-estatico-mdf

Enlaces
=======

- Repositorio GitHub: https://github.com/SanCriolloB/campo-estatico-mdf
- Documentación en línea: (este sitio)
- Streamlit App: https://campo-estatico-mdf.streamlit.app
