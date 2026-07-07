import unittest
import networkx as nx
from src.utils.load_graph import load_graph
from src.scenario.generator import ScenarioGenerator
from src.graph.augment_graph import GraphAugmenter
from src.config import SEED


class TestGraphAugmenter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = load_graph()
        # Generar escenario para pruebas
        generator = ScenarioGenerator(cls.graph, seed=SEED)
        cls.scenario = generator.generate_scenario(num_clients=10)

        # Aumentar grafo
        cls.augmenter = GraphAugmenter(cls.graph)
        cls.result = cls.augmenter.augment(cls.scenario)
        cls.augmented_graph = cls.result.graph

    def test_original_graph_not_changed(self):
        """✓ El grafo original no cambió."""
        depot_id = self.scenario.depot.id
        self.assertNotIn(depot_id, self.graph.nodes)
        for client in self.scenario.clients:
            self.assertNotIn(client.id, self.graph.nodes)

    def test_augmented_graph_node_count(self):
        """✓ El grafo aumentado tiene 11 nodos más (1 depósito + 10 clientes)."""
        expected_node_count = self.graph.number_of_nodes() + 11
        self.assertEqual(self.augmented_graph.number_of_nodes(), expected_node_count)

    def test_depot_exists_as_node(self):
        """✓ El depósito existe como nodo y tiene los atributos correctos."""
        depot_id = self.scenario.depot.id
        self.assertIn(depot_id, self.augmented_graph.nodes)
        node_data = self.augmented_graph.nodes[depot_id]
        self.assertEqual(node_data["kind"], "depot")
        self.assertEqual(node_data["x"], self.scenario.depot.longitude)
        self.assertEqual(node_data["y"], self.scenario.depot.latitude)

    def test_clients_exist_as_nodes(self):
        """✓ Cada cliente existe como nodo y tiene los atributos correctos."""
        for client in self.scenario.clients:
            self.assertIn(client.id, self.augmented_graph.nodes)
            node_data = self.augmented_graph.nodes[client.id]
            self.assertEqual(node_data["kind"], "client")
            self.assertEqual(node_data["x"], client.longitude)
            self.assertEqual(node_data["y"], client.latitude)

    def test_original_edges_still_connected(self):
        """✓ Todas las aristas originales siguen conectadas."""
        # Para cada arista eliminada, verificamos que exista un camino
        # entre sus extremos en el grafo aumentado.
        for edge_tuple in self.result.removed_edges:
            u, v = edge_tuple[0], edge_tuple[1]
            self.assertTrue(
                nx.has_path(self.augmented_graph, u, v),
                f"Se rompió la conectividad original entre {u} y {v}",
            )

    def test_no_disconnected_components_added(self):
        """✓ No quedaron componentes desconectadas nuevas."""
        if self.graph.is_directed():
            original_components = len(list(nx.weakly_connected_components(self.graph)))
            augmented_components = len(
                list(nx.weakly_connected_components(self.augmented_graph))
            )
        else:
            original_components = len(list(nx.connected_components(self.graph)))
            augmented_components = len(
                list(nx.connected_components(self.augmented_graph))
            )
        self.assertEqual(augmented_components, original_components)

    def test_inserted_nodes_have_exactly_two_connections(self):
        """✓ Cada nodo insertado tiene exactamente dos conexiones."""
        for node_id in self.result.inserted_nodes:
            # Grado total = in_degree + out_degree en un grafo dirigido
            total_degree = self.augmented_graph.degree(node_id)
            self.assertEqual(
                total_degree,
                2,
                f"El nodo insertado {node_id} tiene un grado de {total_degree} en lugar de 2",
            )


if __name__ == "__main__":
    unittest.main()
