from collections.abc import Sequence
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt  # noqa: E402
import networkx as nx
import osmnx as ox
from matplotlib.animation import FuncAnimation, PillowWriter  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

matplotlib.use("Agg")

from src.optimization.reconstruct import reconstruct_node_path  # noqa: E402
from src.optimization.vrp import VehicleRoute  # noqa: E402

ROUTE_COLORS = [
    "#2563eb",
    "#16a34a",
    "#f59e0b",
    "#8b5cf6",
    "#ef4444",
    "#0f766e",
    "#ec4899",
    "#64748b",
]


def _render_base_graph(
    graph: nx.MultiDiGraph,
    bgcolor: str = "white",
    edge_color: str = "#d9d9d9",
    edge_linewidth: float = 0.7,
    figsize: tuple[int, int] | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    """
    Renderiza la red vial base sobre un Axes. Reutilizable por plot y animación.
    """
    plot_graph = graph
    if "crs" not in plot_graph.graph:
        plot_graph = graph.copy()
        plot_graph.graph["crs"] = "epsg:4326"

    kwargs: dict = dict(
        node_size=0,
        edge_color=edge_color,
        edge_linewidth=edge_linewidth,
        bgcolor=bgcolor,
        show=False,
        close=False,
    )
    if figsize is not None:
        kwargs["figsize"] = figsize

    return ox.plot_graph(plot_graph, **kwargs)


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


def _collect_interest_points(
    routes: Sequence[VehicleRoute | Sequence[str]],
    graph: nx.MultiDiGraph,
) -> list[tuple[str, str, str]]:
    points: list[tuple[str, str, str]] = []
    seen_nodes: set[str] = set()

    for index, route in enumerate(routes):
        visit_order = _route_to_visit_order(route)
        if not visit_order:
            continue

        color = ROUTE_COLORS[index % len(ROUTE_COLORS)]
        for node_id in visit_order:
            if node_id in seen_nodes or node_id not in graph.nodes:
                continue

            kind = "depot" if node_id == visit_order[0] else "client"
            points.append((node_id, kind, color))
            seen_nodes.add(node_id)

    return points


def _resolve_node_paths(
    graph: nx.MultiDiGraph,
    routes: Sequence[VehicleRoute | Sequence[str]],
    paths: dict[str, dict[str, list]] | None = None,
    route_node_paths: Sequence[Sequence] | None = None,
) -> list[list]:
    if route_node_paths is not None:
        return [list(path) for path in route_node_paths]

    if paths is None:
        raise ValueError("Debe pasarse paths o route_node_paths.")

    return [
        reconstruct_node_path(_route_to_visit_order(route), paths) for route in routes
    ]


def plot_vehicle_routes(
    graph: nx.MultiDiGraph,
    routes: Sequence[VehicleRoute | Sequence[str]],
    paths: dict[str, dict[str, list]] | None = None,
    route_node_paths: Sequence[Sequence] | None = None,
    show: bool = True,
    save_path: str | Path | None = None,
):
    """
    Grafica rutas con estilos más claros y marcadores visibles para cada vehículo.
    """
    fig, ax = _render_base_graph(
        graph, bgcolor="white", edge_color="#d9d9d9", edge_linewidth=0.7
    )

    resolved_node_paths = _resolve_node_paths(
        graph, routes, paths=paths, route_node_paths=route_node_paths
    )
    interest_points = _collect_interest_points(routes, graph)

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
            alpha=0.95,
            solid_capstyle="round",
            label=f"Vehículo {index + 1}",
            zorder=3,
        )

        ax.scatter(
            [xs[0]],
            [ys[0]],
            color="#ffffff",
            edgecolors=color,
            linewidths=1.6,
            s=140,
            marker="o",
            zorder=5,
        )
        ax.scatter(
            [xs[-1]],
            [ys[-1]],
            color=color,
            edgecolors="#111827",
            linewidths=1.2,
            s=140,
            marker="D",
            zorder=5,
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
                    "arrowstyle": "-|>",
                    "color": color,
                    "lw": 1.4,
                    "mutation_scale": 10,
                    "shrinkA": 0,
                    "shrinkB": 0,
                },
                zorder=4,
            )

    for node_id, kind, color in interest_points:
        node_data = graph.nodes[node_id]
        x = node_data.get("x")
        y = node_data.get("y")
        if x is None or y is None:
            continue

        if kind == "depot":
            ax.scatter(
                [x],
                [y],
                s=180,
                marker="D",
                color="#0f172a",
                edgecolors="#ffffff",
                linewidths=1.4,
                zorder=6,
            )
            ax.text(
                x,
                y,
                "D",
                ha="center",
                va="center",
                color="white",
                fontsize=10,
                fontweight="bold",
                zorder=7,
                transform=ax.transData,
            )
        else:
            ax.scatter(
                [x],
                [y],
                s=120,
                marker="o",
                color=color,
                edgecolors="#111827",
                linewidths=1.2,
                zorder=6,
            )
            ax.text(
                x,
                y,
                "C",
                ha="center",
                va="center",
                color="white",
                fontsize=8,
                fontweight="bold",
                zorder=7,
                transform=ax.transData,
            )

    ax.set_title(
        "Mapa de rutas optimizadas",
        fontsize=15,
        fontweight="bold",
        color="#0f172a",
        pad=10,
    )
    if routes:
        legend_handles = [
            Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                markerfacecolor="#16a34a",
                markeredgecolor="#111827",
                markersize=8,
                label="Cliente",
            ),
            Line2D(
                [0],
                [0],
                marker="D",
                color="w",
                markerfacecolor="#0f172a",
                markeredgecolor="#ffffff",
                markersize=8,
                label="Depósito",
            ),
            Line2D([0], [0], color="#2563eb", lw=2.5, label="Vehículo"),
        ]
        ax.legend(
            handles=legend_handles,
            loc="best",
            frameon=True,
            facecolor="white",
            edgecolor="#e2e8f0",
        )

    if save_path is not None:
        fig.savefig(
            save_path, dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor()
        )

    if show:
        plt.show()

    return fig, ax


def plot_vehicle_routes_animation(
    graph: nx.MultiDiGraph,
    routes: Sequence[VehicleRoute | Sequence[str]],
    paths: dict[str, dict[str, list]] | None = None,
    route_node_paths: Sequence[Sequence] | None = None,
    output_path: str | Path | None = None,
    fps: int = 4,
    show: bool = False,
):
    """
    Genera una animación simple en GIF con los vehículos moviéndose sobre cada ruta.
    """
    fig, ax = _render_base_graph(
        graph,
        bgcolor="#f8fafc",
        edge_color="#cbd5e1",
        edge_linewidth=0.8,
        figsize=(10, 8),
    )
    fig.patch.set_facecolor("#f8fafc")
    ax.set_facecolor("#f8fafc")
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    resolved_node_paths = _resolve_node_paths(
        graph, routes, paths=paths, route_node_paths=route_node_paths
    )
    route_coordinates = [
        route_node_path_to_coordinates(graph, node_path)
        for node_path in resolved_node_paths
    ]
    interest_points = _collect_interest_points(routes, graph)

    colors = [
        ROUTE_COLORS[index % len(ROUTE_COLORS)]
        for index in range(len(route_coordinates))
    ]
    car_markers = []

    for index, coordinates in enumerate(route_coordinates):
        if not coordinates:
            continue

        xs = [coord[0] for coord in coordinates]
        ys = [coord[1] for coord in coordinates]
        ax.plot(xs, ys, color=colors[index], linewidth=2.8, alpha=0.95, zorder=3)
        marker = ax.scatter(
            [],
            [],
            s=140,
            marker="o",
            color=colors[index],
            edgecolors="#111827",
            linewidths=1.2,
            zorder=5,
        )
        car_markers.append(marker)

    for node_id, kind, color in interest_points:
        node_data = graph.nodes[node_id]
        x = node_data.get("x")
        y = node_data.get("y")
        if x is None or y is None:
            continue

        if kind == "depot":
            ax.scatter(
                [x],
                [y],
                s=180,
                marker="D",
                color="#0f172a",
                edgecolors="#ffffff",
                linewidths=1.4,
                zorder=6,
            )
            ax.text(
                x,
                y,
                "D",
                ha="center",
                va="center",
                color="white",
                fontsize=10,
                fontweight="bold",
                zorder=7,
            )
        else:
            ax.scatter(
                [x],
                [y],
                s=120,
                marker="o",
                color=color,
                edgecolors="#111827",
                linewidths=1.2,
                zorder=6,
            )
            ax.text(
                x,
                y,
                "C",
                ha="center",
                va="center",
                color="white",
                fontsize=8,
                fontweight="bold",
                zorder=7,
            )

    frame_count = max(
        (len(coordinates) for coordinates in route_coordinates if coordinates),
        default=1,
    )

    def update(frame: int):
        for marker, coordinates in zip(car_markers, route_coordinates):
            if not coordinates:
                continue
            idx = min(frame, len(coordinates) - 1)
            marker.set_offsets([(coordinates[idx][0], coordinates[idx][1])])
        return car_markers

    ax.set_title(
        "Animación de rutas", fontsize=15, fontweight="bold", color="#0f172a", pad=10
    )
    animation = FuncAnimation(
        fig,
        update,
        frames=range(frame_count),
        interval=1000 // max(fps, 1),
        repeat=False,
    )

    if output_path is None:
        output_path = Path("outputs/routes.gif")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    animation.save(output_path, writer=PillowWriter(fps=fps))

    if show:
        plt.show()

    plt.close(fig)
    return output_path
