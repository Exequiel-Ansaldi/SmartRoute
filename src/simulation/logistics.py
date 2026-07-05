from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from src.config import DEFAULT_SERVICE_TIME_SECONDS
from src.optimization.vrp import VehicleRoute

TimeWindow = tuple[float, float]
CongestionModel = Callable[[int, str, str, float, float], float]


@dataclass(slots=True)
class SimulationEvent:
    vehicle_id: int
    event_type: str
    node_id: str
    route_position: int
    start_time: float
    end_time: float
    description: str


@dataclass(slots=True)
class VehicleSimulationSummary:
    vehicle_id: int
    route: list[str]
    start_time: float
    end_time: float
    travel_time: float
    service_time: float
    waiting_time: float
    total_time: float


@dataclass(slots=True)
class SimulationResult:
    events: list[SimulationEvent]
    vehicle_summaries: list[VehicleSimulationSummary]
    bottlenecks: list[SimulationEvent]
    total_time: float


def _normalize_service_times(
    nodes: list[str],
    service_times: dict[str, float] | None,
    depot_index: int,
) -> dict[str, float]:
    normalized = {node: DEFAULT_SERVICE_TIME_SECONDS for node in nodes}
    normalized[nodes[depot_index]] = 0.0

    if service_times is not None:
        normalized.update(service_times)
        normalized[nodes[depot_index]] = 0.0

    return normalized


def _event(
    vehicle_id: int,
    event_type: str,
    node_id: str,
    route_position: int,
    start_time: float,
    end_time: float,
    description: str,
) -> SimulationEvent:
    return SimulationEvent(
        vehicle_id=vehicle_id,
        event_type=event_type,
        node_id=node_id,
        route_position=route_position,
        start_time=start_time,
        end_time=end_time,
        description=description,
    )


def simulate_routes(
    routes: list[VehicleRoute],
    time_matrix: np.ndarray,
    nodes: list[str],
    service_times: dict[str, float] | None = None,
    time_windows: dict[str, TimeWindow] | None = None,
    depot_index: int = 0,
    start_time: float = 0.0,
    congestion_model: CongestionModel | None = None,
    bottleneck_delay_threshold_seconds: float = 300.0,
) -> SimulationResult:
    """
    Simula temporalmente rutas ya optimizadas.

    `time_matrix` debe estar en segundos. El `congestion_model`, si existe,
    recibe (vehicle_id, origin, destination, departure_time, base_travel_time)
    y devuelve demora extra en segundos.
    """
    service_by_node = _normalize_service_times(nodes, service_times, depot_index)
    node_to_index = {node: idx for idx, node in enumerate(nodes)}

    events: list[SimulationEvent] = []
    summaries: list[VehicleSimulationSummary] = []
    bottlenecks: list[SimulationEvent] = []

    for route in routes:
        if len(route.route) == 0:
            continue

        current_time = start_time
        travel_time_total = 0.0
        service_time_total = 0.0
        waiting_time_total = 0.0

        events.append(
            _event(
                route.vehicle_id,
                "departure",
                route.route[0],
                0,
                current_time,
                current_time,
                f"Vehículo {route.vehicle_id} sale de {route.route[0]}",
            )
        )

        for position, (origin, destination) in enumerate(
            zip(route.route, route.route[1:]), start=1
        ):
            origin_idx = node_to_index[origin]
            destination_idx = node_to_index[destination]
            base_travel_time = float(time_matrix[origin_idx, destination_idx])

            if base_travel_time == float("inf"):
                raise ValueError(f"No hay tiempo finito entre {origin} y {destination}.")

            extra_delay = 0.0
            if congestion_model is not None:
                extra_delay = max(
                    0.0,
                    float(
                        congestion_model(
                            route.vehicle_id,
                            origin,
                            destination,
                            current_time,
                            base_travel_time,
                        )
                    ),
                )

            travel_start = current_time
            travel_end = travel_start + base_travel_time + extra_delay
            travel_event = _event(
                route.vehicle_id,
                "travel",
                destination,
                position,
                travel_start,
                travel_end,
                f"{origin} -> {destination}",
            )
            events.append(travel_event)
            travel_time_total += base_travel_time + extra_delay
            current_time = travel_end

            if extra_delay >= bottleneck_delay_threshold_seconds:
                bottlenecks.append(travel_event)

            arrival_event = _event(
                route.vehicle_id,
                "arrival",
                destination,
                position,
                current_time,
                current_time,
                f"Vehículo {route.vehicle_id} llega a {destination}",
            )
            events.append(arrival_event)

            if time_windows and destination in time_windows:
                window_start, window_end = time_windows[destination]
                if current_time > window_end:
                    late_event = _event(
                        route.vehicle_id,
                        "late",
                        destination,
                        position,
                        current_time,
                        current_time,
                        f"Llegada fuera de ventana en {destination}",
                    )
                    events.append(late_event)
                    bottlenecks.append(late_event)
                elif current_time < window_start:
                    wait_start = current_time
                    current_time = window_start
                    wait_event = _event(
                        route.vehicle_id,
                        "wait",
                        destination,
                        position,
                        wait_start,
                        current_time,
                        f"Espera hasta la ventana horaria de {destination}",
                    )
                    events.append(wait_event)
                    waiting_time_total += current_time - wait_start

                    if (
                        current_time - wait_start
                        >= bottleneck_delay_threshold_seconds
                    ):
                        bottlenecks.append(wait_event)

            service_time = service_by_node.get(destination, DEFAULT_SERVICE_TIME_SECONDS)
            if service_time > 0:
                service_start = current_time
                current_time += service_time
                events.append(
                    _event(
                        route.vehicle_id,
                        "service",
                        destination,
                        position,
                        service_start,
                        current_time,
                        f"Servicio en {destination}",
                    )
                )
                service_time_total += service_time

        summaries.append(
            VehicleSimulationSummary(
                vehicle_id=route.vehicle_id,
                route=route.route,
                start_time=start_time,
                end_time=current_time,
                travel_time=travel_time_total,
                service_time=service_time_total,
                waiting_time=waiting_time_total,
                total_time=current_time - start_time,
            )
        )

    total_time = max((summary.total_time for summary in summaries), default=0.0)
    return SimulationResult(
        events=events,
        vehicle_summaries=summaries,
        bottlenecks=bottlenecks,
        total_time=total_time,
    )

