from dataclasses import dataclass
from typing import TypeAlias

NodeId: TypeAlias = int
Edge: TypeAlias = tuple[NodeId, NodeId]


@dataclass(slots=True)
class RoadPoint:
    """
    Representa un punto ubicado sobre una arista del grafo.
    """

    latitude: float
    longitude: float

    edge: Edge

    edge_fraction: float

    node_u: NodeId
    node_v: NodeId

    distance_to_u: float
    distance_to_v: float


@dataclass(slots=True)
class Client(RoadPoint):
    id: str


@dataclass(slots=True)
class Depot(RoadPoint):
    id: str = "depot"


@dataclass(slots=True)
class Scenario:
    seed: int

    depot: Depot

    clients: list[Client]
