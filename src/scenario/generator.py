import random

from shapely.geometry import LineString

from src.config import ALLOWED_HIGHWAYS
from src.scenario.entities import Client, Depot, RoadPoint, Scenario


class ScenarioGenerator:
    """
    Generador de escenarios que encapsula la red vial y maneja la
    generación de clientes y depósito de forma eficiente y reproducible.
    """

    def __init__(self, graph, seed: int | None = None):
        self.graph = graph
        self.seed = seed
        self.rng = random.Random(seed)
        self.valid_edges = self._get_valid_edges()

    def _get_valid_edges(self) -> list:
        """
        Devuelve únicamente las calles donde es válido generar clientes o el depósito.
        """
        valid_edges = []

        for u, v, data in self.graph.edges(data=True):
            highway = data.get("highway")

            if isinstance(highway, list):
                highway = highway[0]

            if highway in ALLOWED_HIGHWAYS:
                valid_edges.append((u, v, data))

        return valid_edges

    def _generate_random_point(self) -> RoadPoint:
        """
        Genera un punto aleatorio sobre una calle válida utilizando el generador
        de números aleatorios local.
        """
        if not self.valid_edges:
            raise ValueError(
                "No hay aristas válidas disponibles en el grafo para generar puntos."
            )

        u, v, data = self.rng.choice(self.valid_edges)

        geometry = data.get("geometry")

        if geometry is None:
            node_u = self.graph.nodes[u]
            node_v = self.graph.nodes[v]

            geometry = LineString(
                [
                    (node_u["x"], node_u["y"]),
                    (node_v["x"], node_v["y"]),
                ]
            )

        edge_length = data["length"]

        distance = self.rng.uniform(0, edge_length)

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

    def generate_clients(self, amount: int) -> list[Client]:
        """
        Genera clientes aleatorios sobre la red vial.
        """
        clients = []

        for i in range(amount):
            road_point = self._generate_random_point()

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

    def generate_depot(self) -> Depot:
        """
        Genera el depósito sobre una calle aleatoria.
        """
        road_point = self._generate_random_point()

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

    def generate_scenario(self, num_clients: int, seed: int | None = None) -> Scenario:
        """
        Genera un escenario completo (depósito + clientes) con opción de
        definir una semilla específica para este escenario.
        """
        actual_seed = seed if seed is not None else self.seed

        if seed is not None:
            self.rng = random.Random(seed)

        depot = self.generate_depot()
        clients = self.generate_clients(num_clients)

        return Scenario(
            seed=actual_seed if actual_seed is not None else 0,
            depot=depot,
            clients=clients,
        )
