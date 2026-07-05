from collections.abc import Sequence
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox

from src.optimization.reconstruct import reconstruct_node_path
from src.optimization.vrp import VehicleRoute

ROUTE_COLORS = [
    "#e41a1c",
    "#377eb8",
    "#4daf4a",
    "#984ea3",
    "#ff7f00",
    "#a65628",
    "#f781bf",
    "#999999",
]


def _edge_coordinates(graph: nx.MultiDiGraph, u, v) -> list[tuple[float, float]]:
    edge_data = graph.get_edge_data(u, v)
    if edge_data:
        best_edge = min(edge_data.values(), key=lambda data: data.get("length", 0.0))
        geometry = best_edge.get("geometry")
        if geometry is not None:
            return list(geometry.coords)

    return [
        (graph.nodes[u]["x"], graph.nodes[u]["y"]),
        (graph.nodes[v]["x"], graph.nodes[v]["y"]),
    ]


def route_node_path_to_coordinates(
    graph: nx.MultiDiGraph, node_path: Sequence
) -> list[tuple[float, float]]:
    """
    Convierte un camino de nodos consecutivos a coordenadas x/y para graficar.
    """
    coordinates: list[tuple[float, float]] = []

    for u, v in zip(node_path, node_path[1:]):
        segment = _edge_coordinates(graph, u, v)
        if coordinates:
            coordinates.extend(segment[1:])
        else:
            coordinates.extend(segment)

    return coordinates


def _route_to_visit_order(route: VehicleRoute | Sequence[str]) -> list[str]:
    if isinstance(route, VehicleRoute):
        return route.route
    return list(route)


def plot_vehicle_routes(
    graph: nx.MultiDiGraph,
    routes: Sequence[VehicleRoute | Sequence[str]],
    paths: dict[str, dict[str, list]] | None = None,
    route_node_paths: Sequence[Sequence] | None = None,
    show: bool = True,
    save_path: str | Path | None = None,
):
    """
    Grafica rutas de uno o varios vehículos sobre el grafo.

    Si se pasan `paths`, cada ruta se interpreta como orden de visitas y se
    reconstruye el camino real. Si se pasan `route_node_paths`, se usan esos
    caminos directamente.
    """
    plot_graph = graph
    if "crs" not in plot_graph.graph:
        plot_graph = graph.copy()
        plot_graph.graph["crs"] = "epsg:4326"

    fig, ax = ox.plot_graph(
        plot_graph,
        node_size=0,
        edge_color="#d9d9d9",
        edge_linewidth=0.6,
        bgcolor="white",
        show=False,
        close=False,
    )

    if route_node_paths is None:
        if paths is None:
            raise ValueError("Debe pasarse paths o route_node_paths.")

        resolved_node_paths = [
            reconstruct_node_path(_route_to_visit_order(route), paths)
            for route in routes
        ]
    else:
        resolved_node_paths = [list(path) for path in route_node_paths]

    for index, node_path in enumerate(resolved_node_paths):
        if len(node_path) < 2:
            continue

        color = ROUTE_COLORS[index % len(ROUTE_COLORS)]
        coordinates = route_node_path_to_coordinates(graph, node_path)
        xs = [coord[0] for coord in coordinates]
        ys = [coord[1] for coord in coordinates]

        ax.plot(
            xs,
            ys,
            color=color,
            linewidth=2.8,
            alpha=0.9,
            label=f"Vehículo {index + 1}",
            zorder=3,
        )

        arrow_step = max(len(coordinates) // 6, 1)
        for arrow_index in range(0, len(coordinates) - 1, arrow_step):
            x1, y1 = coordinates[arrow_index]
            x2, y2 = coordinates[arrow_index + 1]
            ax.annotate(
                "",
                xy=(x2, y2),
                xytext=(x1, y1),
                arrowprops={
                    "arrowstyle": "->",
                    "color": color,
                    "lw": 1.8,
                    "shrinkA": 0,
                    "shrinkB": 0,
                },
                zorder=4,
            )

    if routes:
        ax.legend(loc="best")

    if save_path is not None:
        fig.savefig(save_path, dpi=160, bbox_inches="tight")

    if show:
        plt.show()

    return fig, ax
