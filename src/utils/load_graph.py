import osmnx as ox

GRAPH_PATH = "data/raw/concordia.graphml"


def load_graph():
    return ox.load_graphml(GRAPH_PATH)