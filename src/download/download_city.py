import osmnx as ox

from src.config import CITY, DATA_DIR, GRAPH_PATH, NETWORK_TYPE


def download_city():
    
    """
    Descarga la red vial desde OpenStreetMap.
    """

    G = ox.graph_from_place(
        CITY,
        network_type=NETWORK_TYPE
    )

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    ox.save_graphml(G, str(GRAPH_PATH))

    print(f"Ciudad guardada correctamente en {GRAPH_PATH}.")

    return G


if __name__ == "__main__":
    download_city()
