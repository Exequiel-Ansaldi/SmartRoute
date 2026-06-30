import osmnx as ox
from src.utils.load_graph import load_graph


def plot_city():
    G = load_graph()
    ox.plot_graph(G)


if __name__ == "__main__":
    plot_city()