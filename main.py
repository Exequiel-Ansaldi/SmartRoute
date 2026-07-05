import argparse
from dataclasses import dataclass
from pathlib import Path

from src.config import CLIENTS, NUM_VEHICLES, SEED, VEHICLE_CAPACITY
from src.graph.augment_graph import GraphAugmenter
from src.optimization.tsp import solve_tsp
from src.optimization.vrp import VRPSolution, VehicleRoute, solve_cvrp_nearest_neighbor
from src.routing.matrix import CostMatrixGenerator
from src.scenario.generator import ScenarioGenerator
from src.simulation.logistics import SimulationResult, simulate_routes
from src.utils.load_graph import load_graph
from src.visualization.route_plotter import plot_vehicle_routes


@dataclass(slots=True)
class PipelineResult:
    nodes: list[str]
    routes: list[VehicleRoute]
    solution: VRPSolution | None
    simulation: SimulationResult
    plot_path: Path | None


def run_pipeline(
    clients: int = CLIENTS,
    seed: int = SEED,
    vehicles: int = NUM_VEHICLES,
    capacity: float = VEHICLE_CAPACITY,
    algorithm: str = "vrp",
    output: str | Path | None = None,
    show_plot: bool = False,
) -> PipelineResult:
    graph = load_graph()
    scenario = ScenarioGenerator(graph, seed=seed).generate_scenario(
        num_clients=clients
    )
    augmented_graph = GraphAugmenter(graph).augment(scenario).graph

    matrix_generator = CostMatrixGenerator(augmented_graph)
    distance_matrix, nodes, paths = matrix_generator.generate(scenario, weight="length")
    time_matrix, _, _ = matrix_generator.generate(scenario, weight="travel_time")

    solution: VRPSolution | None = None
    if algorithm == "tsp":
        tsp_solution = solve_tsp(distance_matrix, nodes)
        routes = [
            VehicleRoute(
                vehicle_id=1,
                route_indices=tsp_solution.route_indices,
                route=tsp_solution.route,
                load=float(clients),
                total_cost=tsp_solution.total_cost,
            )
        ]
    elif algorithm == "vrp":
        solution = solve_cvrp_nearest_neighbor(
            distance_matrix,
            nodes,
            vehicle_capacity=capacity,
            num_vehicles=vehicles,
        )
        routes = solution.routes
    else:
        raise ValueError(f"Algoritmo no soportado: {algorithm}")

    simulation = simulate_routes(routes, time_matrix, nodes)

    plot_path = Path(output) if output is not None else None
    if plot_path is not None:
        plot_path.parent.mkdir(parents=True, exist_ok=True)

    plot_vehicle_routes(
        augmented_graph,
        routes,
        paths=paths,
        show=show_plot,
        save_path=plot_path,
    )

    return PipelineResult(
        nodes=nodes,
        routes=routes,
        solution=solution,
        simulation=simulation,
        plot_path=plot_path,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Ejecuta una simulación completa de optimización de rutas."
    )
    parser.add_argument("--clients", type=int, default=CLIENTS)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--vehicles", type=int, default=NUM_VEHICLES)
    parser.add_argument("--capacity", type=float, default=VEHICLE_CAPACITY)
    parser.add_argument("--algorithm", choices=["tsp", "vrp"], default="vrp")
    parser.add_argument("--output", default="outputs/routes.png")
    parser.add_argument("--show-plot", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = run_pipeline(
        clients=args.clients,
        seed=args.seed,
        vehicles=args.vehicles,
        capacity=args.capacity,
        algorithm=args.algorithm,
        output=args.output,
        show_plot=args.show_plot,
    )

    print("\n--- RESULTADO ---")
    print(f"Nodos optimizados: {len(result.nodes)}")
    print(f"Rutas generadas: {len(result.routes)}")
    for route in result.routes:
        print(
            f"Vehículo {route.vehicle_id}: "
            f"{' -> '.join(route.route)} | "
            f"costo={route.total_cost:.2f} | carga={route.load:.2f}"
        )

    if result.solution is not None and result.solution.unassigned:
        print(f"Clientes sin asignar: {', '.join(result.solution.unassigned)}")

    print(f"Tiempo total simulado: {result.simulation.total_time:.2f} s")
    print(f"Cuellos de botella: {len(result.simulation.bottlenecks)}")
    if result.plot_path is not None:
        print(f"Mapa guardado en: {result.plot_path}")


if __name__ == "__main__":
    main()

