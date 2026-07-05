# Optimización de Rutas

Sistema para generar escenarios logísticos sobre un grafo vial de Concordia,
calcular caminos mínimos, optimizar rutas y simular recorridos.

## Instalación

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecución rápida

```powershell
python main.py --clients 5 --vehicles 2 --capacity 10
```

El mapa se guarda por defecto en `outputs/routes.png`.

## Dashboard

```powershell
streamlit run src/dashboard/app.py
```

## Tests

```powershell
python -m unittest discover -s tests
```

Más detalles en `docs/`.

