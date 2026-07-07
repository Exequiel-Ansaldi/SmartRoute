"""Resolvedor VRP/CVRP/VRPTW basado en Google OR-Tools."""

from typing import TypeAlias

import numpy as np
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from src.config import (
    DEFAULT_SERVICE_TIME_SECONDS,
    DEPOT_TIME_WINDOW,
    ORTOOLS_TIME_LIMIT_SECONDS,
)
from src.optimization.tsp import calculate_route_cost
from src.optimization.vrp import VehicleRoute, VRPSolution, _normalize_demands

TimeWindow: TypeAlias = tuple[float, float]

_SCALE = 100


def _to_int(value: float, scale: int = _SCALE) -> int:
    if value == float("inf"):
        raise ValueError("OR-Tools no admite costos infinitos en la matriz.")
    return int(round(value * scale))


def _matrix_to_int(matrix: np.ndarray, scale: int = _SCALE) -> list[list[int]]:
    n = matrix.shape[0]
    return [[_to_int(float(matrix[i, j]), scale) for j in range(n)] for i in range(n)]


def _normalize_service_times(
    nodes: list[str],
    service_times: dict[str, float] | None,
    depot_index: int,
    default_service_time: float,
) -> dict[str, float]:
    normalized = {node: default_service_time for node in nodes}
    normalized[nodes[depot_index]] = 0.0

    if service_times is not None:
        normalized.update(service_times)
        normalized[nodes[depot_index]] = 0.0

    return normalized


def _normalize_time_windows(
    nodes: list[str],
    time_windows: dict[str, TimeWindow] | None,
    depot_index: int,
    depot_time_window: TimeWindow,
) -> dict[str, TimeWindow]:
    if time_windows is None:
        return {}

    normalized = dict(time_windows)
    normalized[nodes[depot_index]] = depot_time_window
    return normalized


def _compute_horizon(
    time_matrix: np.ndarray,
    time_windows: dict[str, TimeWindow],
    service_times: dict[str, float],
    nodes: list[str],
) -> int:
    max_window_end = max(tw[1] for tw in time_windows.values()) if time_windows else 0.0
    finite_values = time_matrix[time_matrix != float("inf")]
    max_travel = float(finite_values.max()) if finite_values.size else 0.0
    total_service = sum(service_times.get(node, 0.0) for node in nodes)
    return _to_int(max_window_end + max_travel * len(nodes) + total_service)


def solve_vrp_ortools(
    matrix: np.ndarray,
    nodes: list[str],
    vehicle_capacity: float,
    num_vehicles: int | None = None,
    demands: dict[str, float] | None = None,
    depot_index: int = 0,
    time_matrix: np.ndarray | None = None,
    time_windows: dict[str, TimeWindow] | None = None,
    service_times: dict[str, float] | None = None,
    depot_time_window: TimeWindow | None = None,
    time_limit_seconds: int | None = None,
) -> VRPSolution:
    """
    Resuelve CVRP o VRPTW con Google OR-Tools.

    Args:
        matrix: Matriz de costos N x N (distancia o tiempo según el objetivo).
        nodes: IDs ordenados (depósito primero por defecto en índice 0).
        vehicle_capacity: Capacidad máxima por vehículo.
        num_vehicles: Cantidad de vehículos disponibles. Si es None, usa len(nodes)-1.
        demands: Demanda por nodo. El depósito debe ser 0.
        depot_index: Índice del depósito en `nodes`.
        time_matrix: Matriz de tiempos de viaje para VRPTW. Si es None y hay ventanas,
            se usa `matrix`.
        time_windows: Ventanas de tiempo por nodo {id: (inicio, fin)} en segundos.
        service_times: Tiempo de servicio por nodo en segundos.
        depot_time_window: Ventana horaria del depósito.
        time_limit_seconds: Límite de búsqueda del solver.

    Returns:
        VRPSolution con rutas, costos y tiempos de llegada si aplica VRPTW.
    """
    if vehicle_capacity <= 0:
        raise ValueError("La capacidad del vehículo debe ser mayor a cero.")

    n = len(nodes)
    if n == 0:
        return VRPSolution(routes=[], total_cost=0.0, unassigned=[])

    fleet_size = num_vehicles if num_vehicles is not None else max(n - 1, 1)
    demand_by_node = _normalize_demands(nodes, demands, depot_index)
    depot = nodes[depot_index]

    for node, demand in demand_by_node.items():
        if node != depot and demand > vehicle_capacity:
            raise ValueError(
                f"La demanda de {node} ({demand}) excede la capacidad del vehículo."
            )

    use_time_windows = time_windows is not None and len(time_windows) > 0
    resolved_depot_window = depot_time_window or DEPOT_TIME_WINDOW
    resolved_time_limit = (
        time_limit_seconds
        if time_limit_seconds is not None
        else ORTOOLS_TIME_LIMIT_SECONDS
    )

    int_matrix = _matrix_to_int(matrix)
    int_capacity = _to_int(vehicle_capacity)

    manager = pywrapcp.RoutingIndexManager(n, fleet_size, depot_index)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index: int, to_index: int) -> int:
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int_matrix[from_node][to_node]

    distance_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(distance_callback_index)

    def demand_callback(from_index: int) -> int:
        from_node = manager.IndexToNode(from_index)
        return _to_int(demand_by_node[nodes[from_node]])

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,
        [int_capacity] * fleet_size,
        True,
        "Capacity",
    )

    normalized_windows: dict[str, TimeWindow] = {}
    normalized_service_times: dict[str, float] = {}

    if use_time_windows:
        travel_matrix = time_matrix if time_matrix is not None else matrix
        if travel_matrix.shape != matrix.shape:
            raise ValueError("time_matrix debe tener la misma forma que matrix.")

        normalized_windows = _normalize_time_windows(
            nodes, time_windows, depot_index, resolved_depot_window
        )
        normalized_service_times = _normalize_service_times(
            nodes, service_times, depot_index, DEFAULT_SERVICE_TIME_SECONDS
        )

        int_time_matrix = _matrix_to_int(travel_matrix)
        int_service_times = [
            _to_int(normalized_service_times[nodes[i]]) for i in range(n)
        ]

        def time_callback(from_index: int, to_index: int) -> int:
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return int_time_matrix[from_node][to_node] + int_service_times[from_node]

        time_callback_index = routing.RegisterTransitCallback(time_callback)
        horizon = _compute_horizon(
            travel_matrix, normalized_windows, normalized_service_times, nodes
        )

        routing.AddDimension(
            time_callback_index,
            horizon,
            horizon,
            False,
            "Time",
        )
        time_dimension = routing.GetDimensionOrDie("Time")

        for node_index, node_id in enumerate(nodes):
            if node_id not in normalized_windows:
                continue

            window_start, window_end = normalized_windows[node_id]
            index = manager.NodeToIndex(node_index)
            time_dimension.CumulVar(index).SetRange(
                _to_int(window_start),
                _to_int(window_end),
            )

        for vehicle_id in range(fleet_size):
            start_index = routing.Start(vehicle_id)
            end_index = routing.End(vehicle_id)
            time_dimension.CumulVar(start_index).SetRange(
                _to_int(resolved_depot_window[0]),
                _to_int(resolved_depot_window[1]),
            )
            time_dimension.CumulVar(end_index).SetRange(
                _to_int(resolved_depot_window[0]),
                _to_int(resolved_depot_window[1]),
            )

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.FromSeconds(resolved_time_limit)

    solution = routing.SolveWithParameters(search_parameters)
    if solution is None:
        return VRPSolution(
            routes=[],
            total_cost=float("inf"),
            unassigned=[node for i, node in enumerate(nodes) if i != depot_index],
        )

    time_dimension = routing.GetDimensionOrDie("Time") if use_time_windows else None
    visited_indices: set[int] = {depot_index}
    routes: list[VehicleRoute] = []

    for vehicle_id in range(fleet_size):
        index = routing.Start(vehicle_id)
        route_indices: list[int] = []
        arrival_times: list[float] = []

        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route_indices.append(node_index)
            visited_indices.add(node_index)

            if time_dimension is not None:
                arrival = solution.Value(time_dimension.CumulVar(index)) / _SCALE
                arrival_times.append(arrival)

            index = solution.Value(routing.NextVar(index))

        end_node = manager.IndexToNode(index)
        if len(route_indices) <= 1:
            continue

        route_indices.append(end_node)
        if time_dimension is not None:
            arrival_times.append(
                solution.Value(time_dimension.CumulVar(index)) / _SCALE
            )

        total_cost = calculate_route_cost(matrix, route_indices)
        routes.append(
            VehicleRoute(
                vehicle_id=vehicle_id + 1,
                route_indices=route_indices,
                route=[nodes[i] for i in route_indices],
                load=sum(demand_by_node[nodes[i]] for i in route_indices[1:-1]),
                total_cost=total_cost,
                arrival_times=arrival_times if use_time_windows else None,
                total_time=(
                    arrival_times[-1] - arrival_times[0]
                    if use_time_windows and arrival_times
                    else None
                ),
            )
        )

    unassigned = [nodes[i] for i in range(n) if i not in visited_indices]
    return VRPSolution(
        routes=routes,
        total_cost=sum(route.total_cost for route in routes),
        unassigned=unassigned,
    )
