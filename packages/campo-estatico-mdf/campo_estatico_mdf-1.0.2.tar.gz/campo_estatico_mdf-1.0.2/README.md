# campo-estatico-mdf

Solver 2D de Laplace por diferencias finitas (Jacobi/Gauss-Seidel) y cálculo del campo eléctrico.  
Incluye GUI en **Streamlit** (multipágina) y documentación **Sphinx** publicada en GitHub Pages.:contentReference[oaicite:0]{index=0}

## Ejecutar GUI (Streamlit)
```bash
# activar entorno
source .venv/Scripts/activate   # Windows (Git Bash)
# pip install dependencias
pip install -r requirements.txt
# instalar paquete backend en editable
pip install -e .
# correr la app
streamlit run app_streamlit/streamlit_app.py
```

### Páginas
- **Simulación**: define N, ε (tolerancia), max_iter, método, y contornos. Muestra `V`, `E` y métricas.
- **Documentación**: enlaza/embebe Sphinx (se publicará en Fase 4). Puedes exportar `DOCS_URL` para mostrarla en la app.

> Si ves problemas con el render de quiver en mallas muy grandes, reduce N o sube el `step` de submuestreo.

# Instalación y Uso del Paquete campo-estatico-mdf

## Instalación desde PyPI

Asegúrate de tener Python 3.9 o superior.

```bash
pip install campo-estatico-mdf
```

> Si prefieres probar una versión de desarrollo local:
> ```bash
> pip install -e .
> ```

---

## Verificación de instalación

Para comprobar que el paquete se instaló correctamente:

```bash
python -m pip show campo-estatico-mdf
```

También puedes verificar desde un intérprete de Python:

```python
from campo_estatico_mdf import LaplaceSolver2D
print(LaplaceSolver2D)
```

Si no hay errores de importación, la instalación es correcta.

---

## Uso rápido

Ejemplo básico para resolver el potencial electrostático 2D por diferencias finitas:

```python
from campo_estatico_mdf import LaplaceSolver2D

# Definir el mallado y condiciones de contorno
N = 51
bc = {"left": 1.0, "right": 0.0, "top": 0.0, "bottom": 1.0}

solver = LaplaceSolver2D(
    N=N,
    bc=bc,
    epsilon=1e-5,
    max_iter=20000,
    method="jacobi", # o "gauss_seidel"
)

V, n_iter, err = solver.solve()
Ex, Ey = solver.compute_e_field(V)

print(f"Iteraciones: {n_iter}, Error final: {err:.3e}")
print("Forma de la matriz de potencial:", V.shape)
```

---

## Dependencias

El paquete requiere **NumPy** (≥1.22). Si no se instaló automáticamente, puedes hacerlo con:

```bash
pip install numpy>=1.22
```

---

## Más información

- Documentación oficial: [https://SanCriolloB.github.io/campo-estatico-mdf/](https://SanCriolloB.github.io/campo-estatico-mdf/)
- Repositorio: [https://github.com/SanCriolloB/campo-estatico-mdf](https://github.com/SanCriolloB/campo-estatico-mdf)

---

**Autores:** Santiago Criollo & Daniel Ramirez 
**Licencia:** MIT  
**Versión:** v1.0.2
