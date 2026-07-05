import heapq
import math
import networkx as nx

from src.config import ASTAR_MAX_SPEED_KPH

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcula la distancia de círculo máximo (Haversine) en metros entre dos
    coordenadas geográficas (latitud, longitud).
    """
    R = 6371000.0  # Radio de la Tierra en metros
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) *
         math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    
    return R * c


def astar_shortest_path(
    graph: nx.MultiDiGraph, source, target, weight: str = "length"
) -> tuple[float, list]:
    """
    Calcula la distancia mínima y el camino completo (lista de nodos)
    desde el nodo origen al nodo destino usando el algoritmo A*.

    Usa la distancia de Haversine como heurística admisible. Si el peso
    es 'travel_time', escala la heurística dividiendo por la velocidad máxima
    permitida en Argentina (130 km/h) para mantener la admisibilidad.

    Args:
        graph: Grafo aumentado (nx.MultiDiGraph).
        source: Nodo origen.
        target: Nodo destino.
        weight: Atributo de costo ('length' o 'travel_time').

    Returns:
        Un tuple (distancia, camino):
        - distancia: costo total (float), inf si no hay camino.
        - camino: lista ordenada de nodos del camino, vacía si no hay camino.
    """
    if source not in graph or target not in graph:
        return float("inf"), []

    if source == target:
        return 0.0, [source]

    target_node = graph.nodes[target]
    target_lat = target_node.get("y")
    target_lon = target_node.get("x")

    # Si el destino no tiene coordenadas, caemos en heurística nula (Dijkstra)
    if target_lat is None or target_lon is None:
        def heuristic(node):
            return 0.0
    else:
        # Velocidad máxima de diseño para mantener admisibilidad al calcular tiempo (m/s)
        max_speed_mps = ASTAR_MAX_SPEED_KPH / 3.6

        if weight == "travel_time":
            def heuristic(node):
                n_data = graph.nodes[node]
                lat = n_data.get("y")
                lon = n_data.get("x")
                if lat is None or lon is None:
                    return 0.0
                dist_m = haversine_distance(lat, lon, target_lat, target_lon)
                return dist_m / max_speed_mps
        else:
            def heuristic(node):
                n_data = graph.nodes[node]
                lat = n_data.get("y")
                lon = n_data.get("x")
                if lat is None or lon is None:
                    return 0.0
                return haversine_distance(lat, lon, target_lat, target_lon)

    # Cola de prioridad: (f_score, g_score, nodo)
    # f_score = g_score + heuristic
    start_h = heuristic(source)
    pq = [(start_h, 0.0, source)]
    
    g_score = {source: 0.0}
    predecessors = {}
    visited = set()

    while pq:
        _, g, u = heapq.heappop(pq)

        if u in visited:
            continue
        visited.add(u)

        if u == target:
            # Reconstruir camino
            path = []
            curr = target
            while curr is not None:
                path.append(curr)
                curr = predecessors.get(curr)
            path.reverse()
            return g, path

        for v in graph.successors(u):
            edge_data_dict = graph.get_edge_data(u, v)
            if not edge_data_dict:
                continue

            # Buscar la arista con el menor peso entre u y v
            min_edge_weight = float("inf")
            for edge_key, data in edge_data_dict.items():
                val = data.get(weight, 0.0)
                val = float(val) if val is not None else 0.0
                if val < min_edge_weight:
                    min_edge_weight = val

            if min_edge_weight == float("inf"):
                continue

            tentative_g_score = g + min_edge_weight

            if v not in g_score or tentative_g_score < g_score[v]:
                g_score[v] = tentative_g_score
                predecessors[v] = u
                h = heuristic(v)
                heapq.heappush(pq, (tentative_g_score + h, tentative_g_score, v))

    return float("inf"), []
