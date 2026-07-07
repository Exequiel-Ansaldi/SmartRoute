from functools import lru_cache

import osmnx as ox

from src.config import GRAPH_PATH


@lru_cache(maxsize=1)
def load_graph():
    return ox.load_graphml(str(GRAPH_PATH))
