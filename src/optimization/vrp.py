from dataclasses import dataclass
from typing import TypedDict

import numpy as np

from src.optimization.tsp import calculate_route_cost


@dataclass(slots=True)
class VehicleRoute:
    vehicle_id: int
    route_indices: list[int]
    route: list[str]
    load: float
    total_cost: float
    arrival_times: list[float] | None = None
    total_time: float | None = None


@dataclass(slots=True)
class VRPSolution:
    routes: list[VehicleRoute]
    total_cost: float
    unassigned: list[str]


class RouteState(TypedDict):
    indices: list[int]
    load: float
    current: int


def _normalize_demands(
    nodes: list[str], demands: dict[str, float] | None, depot_index: int
) -> dict[str, float]:
    normalized = {node: 1.0 for node in nodes}
    normalized[nodes[depot_index]] = 0.0

    if demands is not None:
        normalized.update(demands)
        normalized[nodes[depot_index]] = 0.0

    return normalized


def solve_cvrp_nearest_neighbor(
    matrix: np.ndarray,
    nodes: list[str],
    vehicle_capacity: float,
    num_vehicles: int | None = None,
    demands: dict[str, float] | None = None,
    depot_index: int = 0,
) -> VRPSolution:
    """
    Resuelve un CVRP con una heurística greedy de vecino más cercano por vehículo.
    """
    if vehicle_capacity <= 0:
        raise ValueError("La capacidad del vehículo debe ser mayor a cero.")

    demand_by_node = _normalize_demands(nodes, demands, depot_index)
    depot = nodes[depot_index]

    for node, demand in demand_by_node.items():
        if node != depot and demand > vehicle_capacity:
            raise ValueError(
                f"La demanda de {node} ({demand}) excede la capacidad del vehículo."
            )

    unvisited = set(range(len(nodes)))
    unvisited.remove(depot_index)

    if num_vehicles is not None and num_vehicles > 1:
        multi_vehicle_routes: list[VehicleRoute] = []
        route_states: list[RouteState] = [
            {"indices": [depot_index], "load": 0.0, "current": depot_index}
            for _ in range(num_vehicles)
        ]
        assigned_nodes: set[int] = set()

        for node_idx in sorted(unvisited, key=lambda idx: matrix[depot_index, idx]):
            demand = demand_by_node[nodes[node_idx]]
            feasible_routes: list[tuple[float, float, int, RouteState]] = []

            for route_index, route in enumerate(route_states):
                current_load = float(route["load"])
                if current_load + demand > vehicle_capacity:
                    continue

                route_cost = float(matrix[int(route["current"]), node_idx])
                feasible_routes.append((route_cost, current_load, route_index, route))

            if not feasible_routes:
                best_route = route_states[0]
            else:
                feasible_routes.sort(key=lambda item: (item[1], item[0], item[2]))
                best_route = feasible_routes[0][3]

            best_route["indices"].append(node_idx)
            best_route["load"] = float(best_route["load"]) + demand
            best_route["current"] = node_idx
            assigned_nodes.add(node_idx)

        for vehicle_id, route_state in enumerate(route_states, start=1):
            route_indices = list(route_state["indices"])
            if len(route_indices) <= 1:
                continue

            if matrix[int(route_state["current"]), depot_index] == float("inf"):
                raise ValueError("No hay ruta finita para volver al depósito.")

            route_indices.append(depot_index)
            total_cost = calculate_route_cost(matrix, route_indices)
            multi_vehicle_routes.append(
                VehicleRoute(
                    vehicle_id=vehicle_id,
                    route_indices=route_indices,
                    route=[nodes[i] for i in route_indices],
                    load=float(route_state["load"]),
                    total_cost=total_cost,
                )
            )

        remaining = sorted(unvisited - assigned_nodes)
        if remaining:
            for idx in remaining:
                multi_vehicle_routes[0].route_indices.append(idx)
                multi_vehicle_routes[0].route.append(nodes[idx])
                multi_vehicle_routes[0].load += demand_by_node[nodes[idx]]
                multi_vehicle_routes[0].total_cost = calculate_route_cost(
                    matrix, multi_vehicle_routes[0].route_indices
                )

        return VRPSolution(
            routes=multi_vehicle_routes,
            total_cost=sum(route.total_cost for route in multi_vehicle_routes),
            unassigned=[],
        )

    routes: list[VehicleRoute] = []
    vehicle_id = 1

    while unvisited:
        if num_vehicles is not None and vehicle_id > num_vehicles:
            break

        current = depot_index
        load = 0.0
        route_indices = [depot_index]

        while True:
            feasible = [
                idx
                for idx in unvisited
                if load + demand_by_node[nodes[idx]] <= vehicle_capacity
                and matrix[current, idx] != float("inf")
            ]

            if not feasible:
                break

            next_node = min(feasible, key=lambda idx: matrix[current, idx])
            route_indices.append(next_node)
            load += demand_by_node[nodes[next_node]]
            unvisited.remove(next_node)
            current = next_node

        if len(route_indices) == 1:
            break

        if matrix[current, depot_index] == float("inf"):
            raise ValueError("No hay ruta finita para volver al depósito.")

        route_indices.append(depot_index)
        total_cost = calculate_route_cost(matrix, route_indices)
        routes.append(
            VehicleRoute(
                vehicle_id=vehicle_id,
                route_indices=route_indices,
                route=[nodes[i] for i in route_indices],
                load=load,
                total_cost=total_cost,
            )
        )
        vehicle_id += 1

    unassigned = [nodes[i] for i in sorted(unvisited)]
    return VRPSolution(
        routes=routes,
        total_cost=sum(route.total_cost for route in routes),
        unassigned=unassigned,
    )
