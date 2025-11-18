import os
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Documentación", page_icon="📚", layout="wide")

st.title("📚 Documentación del proyecto (Sphinx)")

st.write(
    """
Esta página muestra y enlaza la documentación técnica generada con **Sphinx** 
para el paquete `campo-estatico-mdf` (versión 1.0.2):

- Fundamento teórico de la ecuación de Laplace 2D y el stencil MDF.
- Descripción de los métodos iterativos (Jacobi y Gauss–Seidel).
- Referencia de la API (`LaplaceSolver2D` y funciones asociadas).
- Tutorial de uso y ejemplos básicos.
- Registro de cambios (changelog) entre versiones.
"""
)

# URL de la documentación Sphinx publicada (GitHub Pages).
# Puede sobreescribirse con la variable de entorno DOCS_URL
DEFAULT_DOCS_URL = "https://SanCriolloB.github.io/campo-estatico-mdf/"
docs_url = os.getenv("DOCS_URL", DEFAULT_DOCS_URL)

st.subheader("Enlaces útiles")

st.markdown(
    f"""
- 🔗 **Documentación oficial (Sphinx / GitHub Pages):** [{docs_url}]({docs_url})
- 💻 **Repositorio en GitHub:** [https://github.com/SanCriolloB/campo-estatico-mdf](https://github.com/SanCriolloB/campo-estatico-mdf)
- 📦 **Paquete en PyPI:** `campo-estatico-mdf`
"""
)

if docs_url:
    st.success(
        "La documentación está publicada y se puede abrir en otra pestaña "
        "o visualizarse embebida en esta página."
    )

    st.markdown(f"🔗 **Abrir documentación en una nueva pestaña:** [{docs_url}]({docs_url})")

    with st.expander("Ver documentación dentro de la app (iframe)"):
        try:
            components.iframe(docs_url, height=900, scrolling=True)
        except Exception as e:
            st.warning(f"No fue posible incrustar el iframe: {e}")
else:
    st.info(
        "Aún no hay URL publicada para la documentación. "
        "Cuando la tengamos, podrás configurarla con la variable "
        "de entorno **DOCS_URL** y se mostrará automáticamente aquí."
    )

st.markdown(
    """
---

ℹ️ **Nota técnica**

La documentación se genera a partir de la carpeta `docs/` del repositorio 
usando **Sphinx** y se publica automáticamente en GitHub Pages. 
Esta misma documentación es la que se enlaza desde esta página.
"""
)
