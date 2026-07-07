import heapq
from itertools import count
from typing import Any

import networkx as nx


def _edge_weight(data: dict, weight: str) -> float:
    value = data.get(weight, 1.0)
    if value is None:
        value = 1.0

    value = float(value)
    if value < 0:
        raise ValueError("Dijkstra no admite aristas con peso negativo.")

    return value


def dijkstra(
    graph: nx.MultiDiGraph, source: Any, target: Any = None, weight: str = "length"
) -> tuple[dict[Any, float], dict[Any, Any]]:
    """
    Ejecuta el algoritmo de Dijkstra desde un nodo origen.
    Si se especifica target, se detiene cuando encuentra el camino más corto a target.

    Args:
        graph: Grafo aumentado (nx.MultiDiGraph).
        source: Nodo origen (ID del nodo).
        target: Nodo destino opcional (ID del nodo).
        weight: Atributo de la arista que se usará como costo ('length' o 'travel_time').

    Returns:
        Un tuple (distancias, predecesores):
        - distancias: dict de nodo -> distancia mínima desde el origen.
        - predecesores: dict de nodo -> nodo anterior en el camino óptimo.
    """
    if source not in graph:
        raise ValueError(f"El nodo origen {source} no existe en el grafo.")

    # Inicializar estructuras
    distances = {source: 0.0}
    predecessors = {}
    
    # Cola de prioridad: almacena tuplas (distancia, nodo)
    counter = count()
    pq = [(0.0, next(counter), source)]
    
    # Conjunto de nodos ya visitados/consolidados
    visited = set()

    while pq:
        dist_u, _, u = heapq.heappop(pq)

        if u in visited:
            continue
        visited.add(u)

        if target is not None and u == target:
            break

        # Iterar sobre los vecinos y las aristas salientes
        for v in graph.successors(u):
            # Obtener todas las aristas paralelas de u a v
            edge_data_dict = graph.get_edge_data(u, v)
            if not edge_data_dict:
                continue

            # Buscar la arista con el menor peso entre u y v
            min_edge_weight = float("inf")
            for data in edge_data_dict.values():
                val = _edge_weight(data, weight)
                if val < min_edge_weight:
                    min_edge_weight = val

            if min_edge_weight == float("inf"):
                continue

            new_dist = dist_u + min_edge_weight
            if v not in distances or new_dist < distances[v]:
                distances[v] = new_dist
                predecessors[v] = u
                heapq.heappush(pq, (new_dist, next(counter), v))

    return distances, predecessors


def dijkstra_path_and_length(
    graph: nx.MultiDiGraph, source, target, weight: str = "length"
) -> tuple[float, list]:
    """
    Calcula la distancia mínima y el camino completo (lista de nodos)
    desde el nodo origen al nodo destino usando Dijkstra.

    Args:
        graph: Grafo aumentado (nx.MultiDiGraph).
        source: Nodo origen.
        target: Nodo destino.
        weight: Atributo de costo.

    Returns:
        Un tuple (distancia, camino):
        - distancia: costo total (float), inf si no hay camino.
        - camino: lista ordenada de nodos del camino, vacía si no hay camino.
    """
    if target not in graph:
        return float("inf"), []

    distances, predecessors = dijkstra(graph, source, target, weight)

    if target not in distances:
        return float("inf"), []

    # Reconstruir camino
    path = []
    curr = target
    while curr is not None:
        path.append(curr)
        curr = predecessors.get(curr)
    
    path.reverse()
    return distances[target], path
