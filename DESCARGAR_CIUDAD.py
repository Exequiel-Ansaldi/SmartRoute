import osmnx as ox

G = ox.graph_from_place(
    "Concordia, Entre Ríos, Argentina",
    network_type="drive"
)
ox.plot_graph(G)