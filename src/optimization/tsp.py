from dataclasses import dataclass

import numpy as np


@dataclass(slots=True)
class TSPSolution:
    route_indices: list[int]
    route: list[str]
    total_cost: float


def calculate_route_cost(matrix: np.ndarray, route_indices: list[int]) -> float:
    """
    Calcula el costo acumulado de recorrer una ruta cerrada o abierta.
    """
    total = 0.0
    for i in range(len(route_indices) - 1):
        cost = float(matrix[route_indices[i], route_indices[i + 1]])
        if cost == float("inf"):
            return float("inf")
        total += cost
    return total


def nearest_neighbor_tsp(
    matrix: np.ndarray, nodes: list[str], depot_index: int = 0
) -> TSPSolution:
    """
    Construye una ruta TSP cerrada usando la heurística de vecino más cercano.
    """
    if len(nodes) == 0:
        return TSPSolution(route_indices=[], route=[], total_cost=0.0)

    unvisited = set(range(len(nodes)))
    unvisited.remove(depot_index)

    route_indices = [depot_index]
    current = depot_index

    while unvisited:
        next_node = min(unvisited, key=lambda idx: matrix[current, idx])
        if matrix[current, next_node] == float("inf"):
            raise ValueError("No hay ruta finita hacia todos los nodos del TSP.")

        route_indices.append(next_node)
        unvisited.remove(next_node)
        current = next_node

    if matrix[current, depot_index] == float("inf"):
        raise ValueError("No hay ruta finita para volver al depósito.")

    route_indices.append(depot_index)
    return TSPSolution(
        route_indices=route_indices,
        route=[nodes[i] for i in route_indices],
        total_cost=calculate_route_cost(matrix, route_indices),
    )


def two_opt(
    matrix: np.ndarray, route_indices: list[int], max_iterations: int = 100
) -> list[int]:
    """
    Mejora una ruta TSP cerrada con búsqueda local 2-opt.
    """
    if len(route_indices) < 5:
        return route_indices.copy()

    best_route = route_indices.copy()
    best_cost = calculate_route_cost(matrix, best_route)

    improved = True
    iterations = 0

    while improved and iterations < max_iterations:
        improved = False
        iterations += 1

        for i in range(1, len(best_route) - 2):
            for j in range(i + 1, len(best_route) - 1):
                candidate = (
                    best_route[:i]
                    + list(reversed(best_route[i : j + 1]))
                    + best_route[j + 1 :]
                )
                candidate_cost = calculate_route_cost(matrix, candidate)

                if candidate_cost < best_cost:
                    best_route = candidate
                    best_cost = candidate_cost
                    improved = True

    return best_route


def solve_tsp(
    matrix: np.ndarray,
    nodes: list[str],
    depot_index: int = 0,
    improve_with_2opt: bool = True,
) -> TSPSolution:
    """
    Resuelve TSP para un vehículo: vecino más cercano y, opcionalmente, 2-opt.
    """
    initial = nearest_neighbor_tsp(matrix, nodes, depot_index)
    route_indices = initial.route_indices

    if improve_with_2opt:
        route_indices = two_opt(matrix, route_indices)

    return TSPSolution(
        route_indices=route_indices,
        route=[nodes[i] for i in route_indices],
        total_cost=calculate_route_cost(matrix, route_indices),
    )
