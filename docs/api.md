# API Principal

## `CostMatrixGenerator`

Genera matrices de distancia o tiempo:

```python
from src.experimental.matrix import CostMatrixGenerator

matrix, nodes, paths = CostMatrixGenerator(graph).generate(scenario, weight="length")
```

También se puede generar ambas matrices (distancia y tiempo) en una sola pasada:

```python
length_matrix, time_matrix, nodes, paths = CostMatrixGenerator(graph).generate_both(scenario)
```

## `dijkstra_two_weights`

Calcula caminos mínimos con dos pesos distintos en un solo recorrido:

```python
from src.experimental.dijkstra import dijkstra_two_weights

dist_a, dist_b, predecessors = dijkstra_two_weights(
    graph, source=u, weight_a="length", weight_b="travel_time"
)
```

## `dijkstra_path_and_length`

Calcula la distancia mínima y el camino usando Dijkstra (deteniéndose en el destino):

```python
from src.experimental.dijkstra import dijkstra_path_and_length

length, path = dijkstra_path_and_length(graph, source, target, weight="length")
```

## `astar_shortest_path`

Calcula el camino mínimo usando A* con heurística de Haversine admisible:

```python
from src.experimental.astar import astar_shortest_path

length, path = astar_shortest_path(graph, source, target, weight="length")
```

## `solve_tsp`

Resuelve una ruta cerrada para un vehículo:

```python
solution = solve_tsp(matrix, nodes)
```

## `solve_cvrp_nearest_neighbor`

Resuelve múltiples vehículos con capacidad:

```python
solution = solve_cvrp_nearest_neighbor(matrix, nodes, vehicle_capacity=10)
```

## `solve_vrp_ortools`

Resuelve CVRP o VRPTW con Google OR-Tools:

```python
solution = solve_vrp_ortools(
    matrix,
    nodes,
    vehicle_capacity=10,
    num_vehicles=2,
    time_matrix=time_matrix,
    time_windows={"client_1": (600, 3600)},
)
```

## `simulate_routes`

Calcula eventos temporales:

```python
simulation = simulate_routes(solution.routes, time_matrix, nodes)
```

