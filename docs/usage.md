# Uso

## Terminal

Ejecutar una simulación VRP:

```powershell
python main.py --clients 5 --vehicles 2 --capacity 10 --algorithm vrp
```

Ejecutar TSP de un vehículo:

```powershell
python main.py --clients 8 --algorithm tsp --output outputs/tsp.png
```

## Dashboard

```powershell
streamlit run src/dashboard/app.py
```

## Tests

```powershell
python -m unittest discover -s tests
```

## Benchmark de Caminos Mínimos (Experimental)

Para comparar el rendimiento en tiempo de ejecución y uso de memoria de Dijkstra personalizado, A* con la heurística de Haversine, y las implementaciones de NetworkX:

```powershell
python -m src.experimental.benchmark
```

