import random

from shapely.geometry import LineString

from src.config import ALLOWED_HIGHWAYS
from src.scenario.entities import Client, Depot, RoadPoint


def _get_valid_edges(graph):
    """
    Devuelve únicamente las calles donde es válido generar clientes.
    """

    valid_edges = []

    for u, v, data in graph.edges(data=True):

        highway = data.get("highway")

        if isinstance(highway, list):
            highway = highway[0]

        if highway in ALLOWED_HIGHWAYS:
            valid_edges.append((u, v, data))

    return valid_edges


def _generate_random_point(graph, valid_edges) -> RoadPoint:
    """
    Genera un punto aleatorio sobre una calle.
    """

    u, v, data = random.choice(valid_edges)

    geometry = data.get("geometry")

    if geometry is None:

        node_u = graph.nodes[u]
        node_v = graph.nodes[v]

        geometry = LineString(
            [
                (node_u["x"], node_u["y"]),
                (node_v["x"], node_v["y"]),
            ]
        )

    edge_length = data["length"]

    distance = random.uniform(0, edge_length)

    edge_fraction = distance / edge_length

    point = geometry.interpolate(
        edge_fraction,
        normalized=True,
    )

    return RoadPoint(
        latitude=point.y,
        longitude=point.x,

        edge=(u, v),

        edge_fraction=edge_fraction,

        node_u=u,
        node_v=v,

        distance_to_u=distance,
        distance_to_v=edge_length - distance,
    )


def generate_clients(graph, amount: int) -> list[Client]:
    """
    Genera clientes aleatorios sobre la red vial.
    """

    valid_edges = _get_valid_edges(graph)

    clients = []

    for i in range(amount):

        road_point = _generate_random_point(
            graph,
            valid_edges,
        )

        clients.append(
            Client(
                id=f"client_{i + 1}",

                latitude=road_point.latitude,
                longitude=road_point.longitude,

                edge=road_point.edge,

                edge_fraction=road_point.edge_fraction,

                node_u=road_point.node_u,
                node_v=road_point.node_v,

                distance_to_u=road_point.distance_to_u,
                distance_to_v=road_point.distance_to_v,
            )
        )

    return clients


def generate_depot(graph) -> Depot:
    """
    Genera el depósito sobre una calle aleatoria.
    """

    valid_edges = _get_valid_edges(graph)

    road_point = _generate_random_point(
        graph,
        valid_edges,
    )

    return Depot(
        latitude=road_point.latitude,
        longitude=road_point.longitude,

        edge=road_point.edge,

        edge_fraction=road_point.edge_fraction,

        node_u=road_point.node_u,
        node_v=road_point.node_v,

        distance_to_u=road_point.distance_to_u,
        distance_to_v=road_point.distance_to_v,
    )