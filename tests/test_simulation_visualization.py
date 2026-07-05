import unittest

import matplotlib
import networkx as nx
import numpy as np

matplotlib.use("Agg")

from src.optimization.vrp import VehicleRoute
from src.simulation.logistics import simulate_routes
from src.visualization.route_plotter import (
    plot_vehicle_routes,
    route_node_path_to_coordinates,
)


class TestLogisticsSimulation(unittest.TestCase):
    def test_simulation_builds_timeline_with_service_and_wait(self):
        nodes = ["depot", "client_1", "client_2"]
        time_matrix = np.array(
            [
                [0, 100, 200],
                [100, 0, 150],
                [200, 150, 0],
            ],
            dtype=float,
        )
        route = VehicleRoute(
            vehicle_id=1,
            route_indices=[0, 1, 2, 0],
            route=nodes + ["depot"],
            load=2,
            total_cost=450,
        )

        result = simulate_routes(
            [route],
            time_matrix,
            nodes,
            service_times={"client_1": 30, "client_2": 40},
            time_windows={"client_2": (400, 1000)},
        )

        event_types = [event.event_type for event in result.events]
        self.assertIn("departure", event_types)
        self.assertIn("travel", event_types)
        self.assertIn("arrival", event_types)
        self.assertIn("wait", event_types)
        self.assertIn("service", event_types)
        self.assertEqual(result.vehicle_summaries[0].waiting_time, 120)
        self.assertEqual(result.vehicle_summaries[0].service_time, 70)

    def test_simulation_flags_congestion_bottleneck(self):
        nodes = ["depot", "client_1"]
        time_matrix = np.array([[0, 100], [100, 0]], dtype=float)
        route = VehicleRoute(
            vehicle_id=1,
            route_indices=[0, 1, 0],
            route=["depot", "client_1", "depot"],
            load=1,
            total_cost=200,
        )

        def congestion_model(vehicle_id, origin, destination, departure, base):
            return 600 if destination == "client_1" else 0

        result = simulate_routes(
            [route],
            time_matrix,
            nodes,
            service_times={"client_1": 0},
            congestion_model=congestion_model,
        )

        self.assertEqual(len(result.bottlenecks), 1)
        self.assertEqual(result.bottlenecks[0].event_type, "travel")


class TestRoutePlotter(unittest.TestCase):
    def test_route_node_path_to_coordinates_uses_graph_nodes(self):
        graph = nx.MultiDiGraph()
        graph.add_node("a", x=0.0, y=0.0)
        graph.add_node("b", x=1.0, y=1.0)
        graph.add_edge("a", "b", length=1.0)

        coordinates = route_node_path_to_coordinates(graph, ["a", "b"])

        self.assertEqual(coordinates, [(0.0, 0.0), (1.0, 1.0)])

    def test_plot_vehicle_routes_returns_figure_and_axis(self):
        graph = nx.MultiDiGraph()
        graph.add_node("depot", x=0.0, y=0.0)
        graph.add_node("client_1", x=1.0, y=1.0)
        graph.add_edge("depot", "client_1", length=1.0)
        graph.add_edge("client_1", "depot", length=1.0)

        route = VehicleRoute(
            vehicle_id=1,
            route_indices=[0, 1, 0],
            route=["depot", "client_1", "depot"],
            load=1,
            total_cost=2,
        )
        paths = {
            "depot": {"client_1": ["depot", "client_1"]},
            "client_1": {"depot": ["client_1", "depot"]},
        }

        fig, ax = plot_vehicle_routes(graph, [route], paths=paths, show=False)

        self.assertIsNotNone(fig)
        self.assertIsNotNone(ax)


if __name__ == "__main__":
    unittest.main()
