# API Principal

## `CostMatrixGenerator`

Genera matrices de distancia o tiempo:

```python
matrix, nodes, paths = CostMatrixGenerator(graph).generate(scenario, weight="length")
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

