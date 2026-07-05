import osmnx as ox

from src.config import GRAPH_PATH


def load_graph():
    return ox.load_graphml(str(GRAPH_PATH))
