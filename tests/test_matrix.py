import unittest

from src.utils.load_graph import load_graph
from src.scenario.generator import ScenarioGenerator
from src.graph.augment_graph import GraphAugmenter
from src.config import SEED
from src.routing.matrix import CostMatrixGenerator


class TestCostMatrixGenerator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = load_graph()
        # Generar un escenario de prueba con 5 clientes
        generator = ScenarioGenerator(cls.graph, seed=SEED)
        cls.scenario = generator.generate_scenario(num_clients=5)

        # Aumentar el grafo
        cls.augmenter = GraphAugmenter(cls.graph)
        cls.result = cls.augmenter.augment(cls.scenario)
        cls.augmented_graph = cls.result.graph

    def test_matrix_dimensions_and_properties(self):
        """✓ La matriz de costo generada posee dimensiones correctas y diagonal nula."""
        generator = CostMatrixGenerator(self.augmented_graph)

        # 1. Distancias (length)
        matrix_dist, nodes_list, paths = generator.generate(
            self.scenario, weight="length"
        )

        num_expected = 1 + len(self.scenario.clients)  # Depósito + 5 clientes = 6
        self.assertEqual(matrix_dist.shape, (num_expected, num_expected))
        self.assertEqual(len(nodes_list), num_expected)
        self.assertEqual(nodes_list[0], self.scenario.depot.id)

        # La diagonal debe ser 0
        for i in range(num_expected):
            self.assertEqual(matrix_dist[i, i], 0.0)

        # 2. Tiempos (travel_time)
        matrix_time, nodes_list, paths_time = generator.generate(
            self.scenario, weight="travel_time"
        )
        self.assertEqual(matrix_time.shape, (num_expected, num_expected))
        for i in range(num_expected):
            self.assertEqual(matrix_time[i, i], 0.0)

        # Verificar que todos los tiempos sean coherentes y mayores a cero para i != j
        for i in range(num_expected):
            for j in range(num_expected):
                if i != j and matrix_time[i, j] != float("inf"):
                    self.assertGreater(matrix_time[i, j], 0.0)
                    self.assertGreater(matrix_dist[i, j], 0.0)

    def test_paths_match_cost_matrix(self):
        """✓ Los caminos reconstruidos coinciden en costo acumulado con la matriz."""
        generator = CostMatrixGenerator(self.augmented_graph)
        matrix, nodes_list, paths = generator.generate(self.scenario, weight="length")

        for i, u in enumerate(nodes_list):
            for j, v in enumerate(nodes_list):
                cost = matrix[i, j]
                path = paths[u].get(v, [])
                if cost == float("inf"):
                    self.assertEqual(len(path), 0)
                else:
                    self.assertNotEqual(len(path), 0)
                    self.assertEqual(path[0], u)
                    self.assertEqual(path[-1], v)

                    # Calcular el costo de recorrer el camino sumando los pesos de sus aristas
                    calculated_cost = 0.0
                    for k in range(len(path) - 1):
                        curr_node = path[k]
                        next_node = path[k + 1]
                        # Obtener la arista de menor longitud entre ambos nodos
                        edge_data = generator.graph.get_edge_data(curr_node, next_node)
                        min_len = min(
                            data.get("length", 0.0) for data in edge_data.values()
                        )
                        calculated_cost += min_len

                    self.assertAlmostEqual(calculated_cost, cost, places=4)


if __name__ == "__main__":
    unittest.main()
