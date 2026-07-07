import unittest

from src.utils.load_graph import load_graph
from src.scenario.generator import ScenarioGenerator
from src.graph.augment_graph import GraphAugmenter
from src.config import SEED
from src.routing.dijkstra import dijkstra_path_and_length
from src.routing.astar import astar_shortest_path, haversine_distance


class TestAStar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = load_graph()
        # Generar un escenario de prueba
        generator = ScenarioGenerator(cls.graph, seed=SEED)
        cls.scenario = generator.generate_scenario(num_clients=5)

        # Aumentar el grafo
        cls.augmenter = GraphAugmenter(cls.graph)
        cls.result = cls.augmenter.augment(cls.scenario)
        cls.augmented_graph = cls.result.graph

    def test_haversine_distance(self):
        """✓ La fórmula de Haversine devuelve valores correctos y positivos."""
        # Distancia aproximada entre Buenos Aires (-34.6037, -58.3816)
        # y Concordia (-31.3922, -58.0201). Debería ser alrededor de 360 km.
        dist = haversine_distance(-34.6037, -58.3816, -31.3922, -58.0201)
        self.assertTrue(350000 < dist < 370000)

        # Distancia a sí mismo es 0
        self.assertEqual(haversine_distance(-31.39, -58.02, -31.39, -58.02), 0.0)

    def test_astar_vs_dijkstra(self):
        """✓ A* produce exactamente las mismas distancias y caminos válidos que Dijkstra."""
        depot_id = self.scenario.depot.id
        client_ids = [c.id for c in self.scenario.clients]
        test_nodes = [depot_id] + client_ids

        for u in test_nodes:
            for v in test_nodes:
                if u == v:
                    continue

                dijkstra_len, dijkstra_path = dijkstra_path_and_length(
                    self.augmented_graph, source=u, target=v, weight="length"
                )
                astar_len, astar_path = astar_shortest_path(
                    self.augmented_graph, source=u, target=v, weight="length"
                )

                self.assertAlmostEqual(dijkstra_len, astar_len, places=4)
                if dijkstra_len != float("inf"):
                    self.assertEqual(dijkstra_path, astar_path)


if __name__ == "__main__":
    unittest.main()
