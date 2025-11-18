# Configuration file for the Sphinx documentation builder.
#
# Para la lista completa de opciones:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# Añadir la raíz del proyecto al path para autodoc
sys.path.insert(0, os.path.abspath('../..'))

# -- Project information -----------------------------------------------------

project = 'campo-estatico-mdf'
copyright = '2025, Santiago Criollo, Daniel Ramirez'
author = 'Santiago Criollo, Daniel Ramirez'

# Versión del proyecto
version = '1.0.2'
release = '1.0.2'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'myst_parser',  # Permitir documentación en Markdown (ej. CHANGELOG.md)
]

templates_path = ['_templates']
exclude_patterns = []

language = 'es'

# Orden de miembros en autodoc
autodoc_member_order = 'bysource'
autoclass_content = 'both'

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Título de la página HTML
html_title = f'{project} {release}'
