import unittest
import networkx as nx
from src.utils.load_graph import load_graph
from src.scenario.generator import ScenarioGenerator
from src.graph.augment_graph import GraphAugmenter
from src.config import SEED
from src.experimental.dijkstra import dijkstra, dijkstra_path_and_length


class TestDijkstra(unittest.TestCase):
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

    def test_dijkstra_vs_networkx(self):
        """✓ Las distancias calculadas con Dijkstra propio coinciden con NetworkX."""
        depot_id = self.scenario.depot.id
        client_ids = [c.id for c in self.scenario.clients]

        # Tomar el depósito y los clientes como puntos de prueba
        test_nodes = [depot_id] + client_ids

        for u in test_nodes:
            for v in test_nodes:
                if u == v:
                    continue
                # Si existe camino en NetworkX, comparar
                try:
                    nx_len = nx.shortest_path_length(
                        self.augmented_graph, source=u, target=v, weight="length"
                    )
                except nx.NetworkXNoPath:
                    custom_len, custom_path = dijkstra_path_and_length(
                        self.augmented_graph, source=u, target=v, weight="length"
                    )
                    self.assertEqual(custom_len, float("inf"))
                    self.assertEqual(len(custom_path), 0)
                    continue

                custom_len, custom_path = dijkstra_path_and_length(
                    self.augmented_graph, source=u, target=v, weight="length"
                )

                self.assertAlmostEqual(custom_len, nx_len, places=4)
                self.assertNotEqual(len(custom_path), 0)
                self.assertEqual(custom_path[0], u)
                self.assertEqual(custom_path[-1], v)

    def test_dijkstra_source_not_in_graph(self):
        """✓ Lanza ValueError si el nodo origen no existe."""
        with self.assertRaises(ValueError):
            dijkstra(self.augmented_graph, "non_existent_node")

    def test_dijkstra_handles_equal_distance_mixed_node_ids(self):
        """✓ No falla si heapq encuentra empates entre IDs de distinto tipo."""
        graph = nx.MultiDiGraph()
        graph.add_edge("origin", 1, length=1.0)
        graph.add_edge("origin", "client", length=1.0)

        distances, _ = dijkstra(graph, "origin", weight="length")

        self.assertEqual(distances[1], 1.0)
        self.assertEqual(distances["client"], 1.0)

    def test_dijkstra_missing_weight_matches_networkx_default(self):
        """✓ Las aristas sin atributo de peso cuestan 1, igual que NetworkX."""
        graph = nx.MultiDiGraph()
        graph.add_edge("a", "b")

        custom_len, custom_path = dijkstra_path_and_length(
            graph, "a", "b", weight="length"
        )

        self.assertEqual(
            custom_len, nx.shortest_path_length(graph, "a", "b", weight="length")
        )
        self.assertEqual(custom_path, ["a", "b"])


if __name__ == "__main__":
    unittest.main()
