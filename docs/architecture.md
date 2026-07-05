# Arquitectura

El proyecto está organizado como una tubería de datos:

1. `src/download`: descarga el grafo vial desde OpenStreetMap.
2. `src/scenario`: genera depósito y clientes reproducibles sobre aristas.
3. `src/graph`: inserta esos puntos en el grafo sin mutar el original.
4. `src/routing`: calcula caminos mínimos, tiempos y matrices de costo.
5. `src/optimization`: decide el orden de visita para TSP, CVRP y VRPTW.
6. `src/simulation`: transforma rutas en eventos temporales.
7. `src/visualization`: grafica rutas sobre el mapa.
8. `main.py` y `src/dashboard/app.py`: puntos de entrada para uso final.

La configuración global vive en `src/config.py`.

