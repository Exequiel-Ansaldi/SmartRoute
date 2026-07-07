import numpy as np

from main import solve_routes_for_algorithm


def test_solve_routes_for_algorithm_supports_tsp_and_vrp():
    matrix = np.array(
        [
            [0.0, 1.0, 2.0],
            [1.0, 0.0, 1.0],
            [2.0, 1.0, 0.0],
        ]
    )
    nodes = ["depot", "client_1", "client_2"]

    routes, solution = solve_routes_for_algorithm(
        matrix,
        nodes,
        clients=2,
        vehicles=1,
        capacity=10.0,
        algorithm="tsp",
    )

    assert len(routes) == 1
    assert routes[0].route[0] == "depot"
    assert routes[0].route[-1] == "depot"

    routes_vrp, solution_vrp = solve_routes_for_algorithm(
        matrix,
        nodes,
        clients=2,
        vehicles=1,
        capacity=10.0,
        algorithm="vrp",
    )

    assert len(routes_vrp) == 1
    assert solution_vrp is not None


def test_vrp_uses_multiple_routes_when_requested():
    matrix = np.array(
        [
            [0.0, 1.0, 2.0, 3.0, 4.0],
            [1.0, 0.0, 1.0, 2.0, 3.0],
            [2.0, 1.0, 0.0, 1.0, 2.0],
            [3.0, 2.0, 1.0, 0.0, 1.0],
            [4.0, 3.0, 2.0, 1.0, 0.0],
        ]
    )
    nodes = ["depot", "client_1", "client_2", "client_3", "client_4"]

    routes, solution = solve_routes_for_algorithm(
        matrix,
        nodes,
        clients=4,
        vehicles=2,
        capacity=10.0,
        algorithm="vrp",
    )

    assert len(routes) == 2
    assert solution is not None
    assert all(route.route[0] == "depot" for route in routes)
    assert all(route.route[-1] == "depot" for route in routes)
