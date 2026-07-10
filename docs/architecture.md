# Arquitectura

El proyecto está organizado como una tubería de datos:

1. `src/download`: descarga el grafo vial desde OpenStreetMap.
2. `src/scenario`: genera depósito y clientes reproducibles sobre aristas.
3. `src/graph`: inserta esos puntos en el grafo sin mutar el original.
4. `src/experimental`: calcula caminos mínimos (Dijkstra y A* propios), tiempos y matrices de costo.
5. `src/optimization`: decide el orden de visita para TSP, CVRP y VRPTW.
6. `src/simulation`: transforma rutas en eventos temporales.
7. `src/visualization`: grafica rutas sobre el mapa.
8. `main.py` y `src/dashboard/app.py`: puntos de entrada para uso final.

### Módulos Experimentales de Rutas
Para el cálculo de caminos mínimos sobre el grafo vial, se desarrollaron algoritmos a medida optimizados en rendimiento frente a las implementaciones estándar de NetworkX:
- **Dijkstra personalizado** (`src/experimental/dijkstra.py`): Permite buscar caminos mínimos deteniéndose opcionalmente al encontrar el destino.
- **A\* personalizado** (`src/experimental/astar.py`): Emplea la distancia de Haversine como heurística admisible (escalada si se mide por tiempo de viaje) para acelerar significativamente la búsqueda.
- **Matriz de Costos** (`src/experimental/matrix.py`): Genera eficientemente matrices de costo y tiempo utilizando Dijkstra de una sola fuente para los clientes y el depósito.
- **Benchmark** (`src/experimental/benchmark.py`): Compara el rendimiento en tiempo y memoria de las diferentes alternativas de búsqueda.

La configuración global vive en `src/config.py`.

