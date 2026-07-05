import unittest

from src.config import SEED
from src.scenario.generator import ScenarioGenerator
from src.utils.load_graph import load_graph


def scenario_signature(scenario):
    points = [scenario.depot] + scenario.clients
    return [
        (
            point.id,
            point.edge,
            round(point.edge_fraction, 12),
            round(point.latitude, 12),
            round(point.longitude, 12),
        )
        for point in points
    ]


class TestScenarioGenerator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = load_graph()

    def test_same_seed_generates_same_spots(self):
        """✓ La misma semilla genera exactamente los mismos puntos."""
        scenario_a = ScenarioGenerator(self.graph, seed=SEED).generate_scenario(
            num_clients=10
        )
        scenario_b = ScenarioGenerator(self.graph, seed=SEED).generate_scenario(
            num_clients=10
        )

        self.assertEqual(scenario_signature(scenario_a), scenario_signature(scenario_b))

    def test_different_seed_generates_different_spots(self):
        """✓ Semillas distintas generan puntos distintos."""
        scenario_a = ScenarioGenerator(self.graph, seed=SEED).generate_scenario(
            num_clients=10
        )
        scenario_b = ScenarioGenerator(self.graph, seed=SEED + 1).generate_scenario(
            num_clients=10
        )

        self.assertNotEqual(
            scenario_signature(scenario_a), scenario_signature(scenario_b)
        )

    def test_generated_points_are_not_repeated_in_same_scenario(self):
        """✓ Depósito y clientes no caen en el mismo spot exacto."""
        scenario = ScenarioGenerator(self.graph, seed=SEED).generate_scenario(
            num_clients=20
        )
        spots = [
            (
                point.edge,
                round(point.edge_fraction, 12),
                round(point.latitude, 12),
                round(point.longitude, 12),
            )
            for point in [scenario.depot] + scenario.clients
        ]

        self.assertEqual(len(spots), len(set(spots)))


if __name__ == "__main__":
    unittest.main()
