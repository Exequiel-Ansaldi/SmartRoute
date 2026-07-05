import unittest

import numpy as np

from src.optimization.reconstruct import reconstruct_edge_path, reconstruct_node_path
from src.optimization.tsp import calculate_route_cost, solve_tsp, two_opt
from src.optimization.vrp import solve_cvrp_nearest_neighbor


class TestTSP(unittest.TestCase):
    def test_solve_tsp_visits_all_clients_and_returns_to_depot(self):
        matrix = np.array(
            [
                [0, 2, 9, 10],
                [1, 0, 6, 4],
                [15, 7, 0, 8],
                [6, 3, 12, 0],
            ],
            dtype=float,
        )
        nodes = ["depot", "client_1", "client_2", "client_3"]

        solution = solve_tsp(matrix, nodes)

        self.assertEqual(solution.route[0], "depot")
        self.assertEqual(solution.route[-1], "depot")
        self.assertEqual(set(solution.route[1:-1]), set(nodes[1:]))
        self.assertEqual(len(solution.route), len(nodes) + 1)
        self.assertEqual(
            solution.total_cost, calculate_route_cost(matrix, solution.route_indices)
        )

    def test_two_opt_does_not_make_route_worse(self):
        matrix = np.array(
            [
                [0, 10, 1, 10],
                [10, 0, 10, 1],
                [1, 10, 0, 10],
                [10, 1, 10, 0],
            ],
            dtype=float,
        )
        route = [0, 1, 2, 3, 0]

        improved = two_opt(matrix, route)

        self.assertLessEqual(
            calculate_route_cost(matrix, improved), calculate_route_cost(matrix, route)
        )


class TestCVRP(unittest.TestCase):
    def test_cvrp_respects_vehicle_capacity(self):
        matrix = np.array(
            [
                [0, 2, 3, 4],
                [2, 0, 1, 5],
                [3, 1, 0, 6],
                [4, 5, 6, 0],
            ],
            dtype=float,
        )
        nodes = ["depot", "client_1", "client_2", "client_3"]

        solution = solve_cvrp_nearest_neighbor(
            matrix, nodes, vehicle_capacity=2, num_vehicles=2
        )

        self.assertEqual(solution.unassigned, [])
        self.assertEqual(len(solution.routes), 2)
        for route in solution.routes:
            self.assertLessEqual(route.load, 2)
            self.assertEqual(route.route[0], "depot")
            self.assertEqual(route.route[-1], "depot")

    def test_cvrp_reports_unassigned_when_vehicle_limit_is_insufficient(self):
        matrix = np.array(
            [
                [0, 2, 3, 4],
                [2, 0, 1, 5],
                [3, 1, 0, 6],
                [4, 5, 6, 0],
            ],
            dtype=float,
        )
        nodes = ["depot", "client_1", "client_2", "client_3"]

        solution = solve_cvrp_nearest_neighbor(
            matrix, nodes, vehicle_capacity=1, num_vehicles=2
        )

        self.assertEqual(len(solution.unassigned), 1)


from src.optimization.ortools_solver import solve_vrp_ortools
from src.optimization.vrp import solve_cvrp_nearest_neighbor


class TestORToolsVRP(unittest.TestCase):
    def test_ortools_cvrp_respects_vehicle_capacity(self):
        matrix = np.array(
            [
                [0, 2, 3, 4],
                [2, 0, 1, 5],
                [3, 1, 0, 6],
                [4, 5, 6, 0],
            ],
            dtype=float,
        )
        nodes = ["depot", "client_1", "client_2", "client_3"]

        solution = solve_vrp_ortools(
            matrix, nodes, vehicle_capacity=2, num_vehicles=2
        )

        self.assertEqual(solution.unassigned, [])
        self.assertGreaterEqual(len(solution.routes), 1)
        for route in solution.routes:
            self.assertLessEqual(route.load, 2)
            self.assertEqual(route.route[0], "depot")
            self.assertEqual(route.route[-1], "depot")

    def test_ortools_vrptw_respects_time_windows(self):
        # Tiempos de viaje en segundos
        time_matrix = np.array(
            [
                [0, 600, 300, 900],
                [600, 0, 400, 500],
                [300, 400, 0, 600],
                [900, 500, 600, 0],
            ],
            dtype=float,
        )
        nodes = ["depot", "client_1", "client_2", "client_3"]
        time_windows = {
            "depot": (0, 86400),
            "client_1": (1200, 7200),
            "client_2": (600, 5400),
            "client_3": (2400, 10800),
        }

        solution = solve_vrp_ortools(
            matrix=time_matrix,
            nodes=nodes,
            vehicle_capacity=10,
            num_vehicles=2,
            time_matrix=time_matrix,
            time_windows=time_windows,
            service_times={"client_1": 60, "client_2": 60, "client_3": 60},
        )

        self.assertEqual(solution.unassigned, [])
        for route in solution.routes:
            self.assertIsNotNone(route.arrival_times)
            for node_id, arrival in zip(route.route, route.arrival_times):
                if node_id in time_windows:
                    start, end = time_windows[node_id]
                    self.assertGreaterEqual(arrival, start)
                    self.assertLessEqual(arrival, end)


class TestRouteReconstruction(unittest.TestCase):
    def test_reconstruct_node_path_concatenates_saved_segments(self):
        paths = {
            "depot": {"client_1": ["depot", 1, 2, "client_1"]},
            "client_1": {"client_2": ["client_1", 3, "client_2"]},
            "client_2": {"depot": ["client_2", 4, "depot"]},
        }

        node_path = reconstruct_node_path(
            ["depot", "client_1", "client_2", "depot"], paths
        )

        self.assertEqual(
            node_path, ["depot", 1, 2, "client_1", 3, "client_2", 4, "depot"]
        )

    def test_reconstruct_edge_path_returns_consecutive_edges(self):
        paths = {
            "depot": {"client_1": ["depot", 1, "client_1"]},
            "client_1": {"depot": ["client_1", 2, "depot"]},
        }

        edge_path = reconstruct_edge_path(["depot", "client_1", "depot"], paths)

        self.assertEqual(
            edge_path,
            [("depot", 1), (1, "client_1"), ("client_1", 2), (2, "depot")],
        )


if __name__ == "__main__":
    unittest.main()
