import osmnx as ox
import networkx as nx


class GraphPlotter:
    """
    Clase responsable de la visualización de los grafos viales y sus
    escenarios asociados (depósito y clientes).
    """

    def __init__(self, edge_color: str = "#888888", edge_linewidth: float = 0.8):
        self.edge_color = edge_color
        self.edge_linewidth = edge_linewidth

    def plot(self, graph: nx.MultiDiGraph) -> None:
        """
        Dibuja el grafo mostrando:
        - Calles en gris.
        - Depósito en azul.
        - Clientes en rojo.
        - Nodos originales pequeños y en gris claro.
        """
        node_colors = []
        node_sizes = []

        for _, data in graph.nodes(data=True):
            kind = data.get("kind")
            if kind == "depot":
                node_colors.append("#1f77b4")  # Azul llamativo para el depósito
                node_sizes.append(120)        # Depósito grande
            elif kind == "client":
                node_colors.append("#d62728")  # Rojo llamativo para los clientes
                node_sizes.append(70)         # Clientes medianos
            else:
                node_colors.append("#e0e0e0")  # Gris muy claro para nodos originales
                node_sizes.append(10)         # Nodos originales muy pequeños

        # Graficar usando la utilidad de visualización nativa de OSMnx
        ox.plot_graph(
            graph,
            node_color=node_colors,
            node_size=node_sizes,
            edge_color=self.edge_color,
            edge_linewidth=self.edge_linewidth,
            show=True
        )


if __name__ == "__main__":
    import sys
    import os

    # Añadir el directorio raíz del proyecto al sys.path para poder correrlo directamente
    sys.path.append(
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    )

    from src.utils.load_graph import load_graph
    from src.scenario.generator import ScenarioGenerator
    from src.graph.augment_graph import GraphAugmenter
    from src.config import CLIENTS, SEED

    print("1. Cargando grafo...")
    G = load_graph()

    print(f"2. Generando escenario con {CLIENTS} clientes...")
    generator = ScenarioGenerator(G, seed=SEED)
    scenario = generator.generate_scenario(num_clients=CLIENTS)

    print("3. Aumentando grafo...")
    augmenter = GraphAugmenter(G)
    result = augmenter.augment(scenario)

    print("4. Graficando mapa aumentado...")
    plotter = GraphPlotter()
    plotter.plot(result.graph)
