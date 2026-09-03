# Finanzas de los hogares colombianos

Dashboard interactivo para explorar ingresos, gastos y capacidad de ahorro de una muestra de hogares en Colombia. Convierte datos tabulares en indicadores ejecutivos, comparaciones regionales e insights fáciles de interpretar.

**Demo:** [finanzas-docker.onrender.com](https://finanzas-docker.onrender.com/)

## Funcionalidades

- Panel ejecutivo con indicadores financieros y filtros globales.
- Distribuciones, boxplots, correlaciones y segmentación por ingreso.
- Comparación y mapa regional con indicadores seleccionables.
- Insights automáticos que reaccionan a los filtros.
- Explorador, controles de calidad y descarga de datos.
- Diseño responsive y despliegue reproducible con Docker.

## Stack

Python 3.10 · Streamlit · pandas · Plotly · Docker · Render

## Ejecución local

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

La aplicación estará en `http://localhost:8501`.

## Docker

```bash
docker build -t finanzas-hogares .
docker run --rm -p 8501:8501 finanzas-hogares
```

## Indicadores derivados

- **Gasto esencial:** alimentación + educación.
- **Balance disponible:** ingreso menos gasto esencial.
- **Tasa de ahorro:** ahorro / ingreso.
- **Carga de gastos:** gasto esencial / ingreso.
- **Segmento de ingreso:** cuartil de la muestra completa.

## Nota sobre los datos

Es un análisis descriptivo de una muestra demostrativa de 200 hogares en 10 departamentos. No representa una estimación oficial para toda Colombia.
