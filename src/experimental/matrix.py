import re
from typing import cast

import networkx as nx
import numpy as np
from src.config import DEFAULT_SPEED_KPH, DEFAULT_SPEEDS_KPH
from src.scenario.entities import Scenario
from src.experimental.dijkstra import dijkstra


def parse_maxspeed(maxspeed_val) -> float | None:
    """
    Parsea de forma robusta el atributo maxspeed de OpenStreetMap a km/h.
    Soporta enteros, floats, strings y listas de valores.
    """
    if maxspeed_val is None:
        return None
    if isinstance(maxspeed_val, list):
        parsed = [parse_maxspeed(x) for x in maxspeed_val]
        valid = [x for x in parsed if x is not None]
        return sum(valid) / len(valid) if valid else None

    if isinstance(maxspeed_val, (int, float)):
        return float(maxspeed_val)

    val_str = str(maxspeed_val).strip().lower()
    match = re.search(r"\d+", val_str)
    if not match:
        return None

    speed = float(match.group())
    if "mph" in val_str:
        speed = speed * 1.60934

    return speed


def get_edge_speed(edge_data) -> float:
    """
    Obtiene la velocidad permitida para una arista.
    Si no posee maxspeed, deduce una velocidad según el tipo de calle.
    """
    maxspeed_val = edge_data.get("maxspeed")
    speed = parse_maxspeed(maxspeed_val)
    if speed is not None:
        return speed

    highway = edge_data.get("highway", "unclassified")
    if isinstance(highway, list):
        highway = highway[0]

    return DEFAULT_SPEEDS_KPH.get(highway, DEFAULT_SPEED_KPH)


def add_travel_times_to_graph(graph: nx.MultiDiGraph) -> None:
    """
    Agrega los atributos 'speed_kph' y 'travel_time' en segundos a todas las aristas del grafo.
    """
    for u, v, key, data in graph.edges(keys=True, data=True):
        speed_kph = get_edge_speed(data)
        # Evitar división por cero o velocidades negativas
        if speed_kph <= 0:
            speed_kph = DEFAULT_SPEED_KPH

        speed_mps = speed_kph / 3.6
        length = float(data.get("length", 0.0))

        travel_time = length / speed_mps
        data["speed_kph"] = speed_kph
        data["travel_time"] = travel_time


class CostMatrixGenerator:
    """
    Clase para calcular matrices de costos (distancias o tiempos)
    entre el depósito y los clientes usando el grafo vial de forma óptima.
    """

    def __init__(self, graph: nx.MultiDiGraph):
        # Crear una copia interna para no mutar el grafo original externamente
        self.graph = cast(nx.MultiDiGraph, graph.copy())
        add_travel_times_to_graph(self.graph)

    def generate(
        self, scenario: Scenario, weight: str = "length"
    ) -> tuple[np.ndarray, list[str], dict[str, dict[str, list]]]:
        """
        Genera la matriz de costos y guarda todos los caminos mínimos entre el depósito
        y los clientes.

        Args:
            scenario: Escenario con el depósito y la lista de clientes.
            weight: Atributo de costo ('length' o 'travel_time').

        Returns:
            Un tuple (matrix, nodes_list, paths):
            - matrix: np.ndarray de N x N con los costos mínimos de viaje.
            - nodes_list: lista ordenada con los IDs de los nodos (el depósito va primero).
            - paths: dict de la forma paths[u][v] = [u, node1, node2, ..., v] con el camino.
        """
        # Identificar depósito e IDs de clientes
        depot_id = scenario.depot.id
        client_ids = [c.id for c in scenario.clients]

        # El orden del índice de la matriz es: primero el depósito, luego los clientes
        nodes_list = [depot_id] + client_ids
        N = len(nodes_list)

        # Inicializar matriz de costos
        matrix = np.full((N, N), float("inf"))

        # Inicializar diccionario de caminos
        paths = {u: {} for u in nodes_list}

        # Ejecutar Dijkstra de una sola fuente para cada nodo en nodes_list
        for i, u in enumerate(nodes_list):
            matrix[i, i] = 0.0
            paths[u][u] = [u]

            if u not in self.graph:
                # Si el nodo no está en el grafo por alguna razón, se deja con infinito
                continue

            distances, predecessors = dijkstra(
                self.graph, source=u, target=None, weight=weight
            )

            for j, v in enumerate(nodes_list):
                if u == v:
                    continue

                if v in distances:
                    matrix[i, j] = distances[v]

                    # Reconstruir camino desde v hasta u usando predecessors
                    path = []
                    curr = v
                    while curr is not None:
                        path.append(curr)
                        curr = predecessors.get(curr)
                    path.reverse()

                    # Verificar que el camino realmente inicie en u (por seguridad de conectividad)
                    if path and path[0] == u:
                        paths[u][v] = path
                    else:
                        paths[u][v] = []
                else:
                    matrix[i, j] = float("inf")
                    paths[u][v] = []

        return matrix, nodes_list, paths
