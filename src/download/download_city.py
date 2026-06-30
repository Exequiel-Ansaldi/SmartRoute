import os
import osmnx as ox

CITY = "Concordia, Entre Ríos, Argentina"

DATA_DIR = "data/raw"
GRAPH_FILE = os.path.join(DATA_DIR, "concordia.graphml")


def download_city():
    
    """
    Descarga la red vial desde OpenStreetMap.
    """

    G = ox.graph_from_place(
        CITY,
        network_type="drive"
    )

    os.makedirs(DATA_DIR, exist_ok=True)

    ox.save_graphml(G, GRAPH_FILE)

    print("Ciudad guardada correctamente.")

    return G


if __name__ == "__main__":
    download_city()