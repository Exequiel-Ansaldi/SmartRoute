# Optimización de Rutas

Sistema de optimización de rutas desarrollado sobre un grafo vial real de la ciudad de Concordia, Entre Ríos.
El proyecto permite generar escenarios logísticos, calcular caminos mínimos, optimizar recorridos de vehículos y visualizar los resultados mediante un dashboard interactivo.

## Instalación

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

# Dashboard

El sistema cuenta con un dashboard interactivo para explorar:

Visualización del grafo vial.
Generación de clientes y depósitos sobre calles reales.
Cálculo de rutas óptimas.
Visualización de recorridos de vehículos.
Métricas de distancia, tiempo y eficiencia.
Simulación del proceso logístico.

## Ejecutar dashboard

```bash
streamlit run src/dashboard/app.py
```

El dashboard se abrirá automáticamente en el navegador.

## Procesamiento geográfico

- Descarga y construcción del grafo vial utilizando datos reales de OpenStreetMap.
- Modelado de calles mediante grafos dirigidos.
- Análisis de conectividad y características de la red vial.

## Generación de escenarios

Permite crear escenarios logísticos con:

- Depósito inicial.
- Clientes distribuidos sobre calles reales.
- Cantidad configurable de vehículos.
- Restricciones de capacidad.

## Tests

```powershell
python -m unittest discover -s tests
```

Más detalles en `docs/`.

