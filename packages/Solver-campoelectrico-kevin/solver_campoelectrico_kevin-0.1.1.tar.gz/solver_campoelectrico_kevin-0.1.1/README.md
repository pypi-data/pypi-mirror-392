# Taller Avanzado: Solución del Campo Electroestático 2D

Este proyecto implementa un solver para la Ecuación de Laplace en 2D usando el Método de Diferencias Finitas (MDF) y el método iterativo de Jacobi. Incluye una interfaz gráfica con Streamlit para visualizar los resultados.

## Estructura del Proyecto

- `src/campo_estatico_mdf`: El paquete Python con la lógica científica (`solver.py`).
- `tests/`: Pruebas unitarias con `pytest`.
- `app.py`: La interfaz de usuario web con Streamlit.
- `docs/`: Carpeta para la documentación generada con Sphinx.
- `.github/workflows`: Automatización para desplegar la documentación en GitHub Pages.

## Cómo empezar

### 1. Requisitos

- Python 3.8 o superior
- Git

### 2. Configuración del Entorno

```bash
# Clona el repositorio (si lo subes a GitHub)
# git clone ...
# cd taller_electrostatica

# Crea un entorno virtual
python -m venv .venv

# Activa el entorno
# En Linux/macOS:
source .venv/bin/activate
# En Windows:
# .\.venv\Scripts\activate

# Instala el paquete y todas las dependencias de desarrollo
pip install -e .[dev]
