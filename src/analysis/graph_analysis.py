from collections import Counter
import networkx as nx
from src.utils.load_graph import load_graph

def analyze_graph():
    G = load_graph()
    print("=" * 60)
    print("ANÁLISIS DE LA RED VIAL")
    print("=" * 60)

    print(f"Nodos   : {G.number_of_nodes()}")
    print(f"Aristas : {G.number_of_edges()}")

    # ==========================
    # Longitud total
    # ==========================

    total_length = 0

    for _, _, data in G.edges(data=True):
        total_length += data.get("length", 0)

    print(f"\nLongitud total: {total_length / 1000:.2f} km")

    average = total_length / G.number_of_edges()

    print(f"Longitud promedio: {average:.2f} metros")

    # ==========================
    # Tipos de calles
    # ==========================

    road_counter = Counter()

    for _, _, data in G.edges(data=True):
        road = data.get("highway")

        if road is None:
            continue

        if isinstance(road, list):
            road = road[0]

        road_counter[road] += 1

    print("\nTipos de calles\n")

    for road, count in road_counter.most_common():
        print(f"{road:20} {count}")

    # ==========================
    # Sentidos de circulación
    # ==========================

    oneway = 0
    twoway = 0

    for _, _, data in G.edges(data=True):
        if data.get("oneway", False):
            oneway += 1
        else:
            twoway += 1

    total = oneway + twoway

    print("\nSentidos de circulación\n")
    print(f"Un sentido : {100 * oneway / total:.1f}%")
    print(f"Doble mano : {100 * twoway / total:.1f}%")

    # ==========================
    # Nodo con mayor conectividad
    # ==========================

    degrees = dict(G.degree())

    best_node = max(degrees, key=degrees.get)

    print("\nNodo con mayor conectividad")
    print(best_node)
    print(degrees[best_node])

    # ==========================
    # Distribución de conexiones
    # ==========================

    degree_counter = Counter(degrees.values())

    print("\nDistribución de conexiones")

    for degree, amount in sorted(degree_counter.items()):
        print(f"{degree} conexiones -> {amount} nodos")

    # ==========================
    # Calles más largas
    # ==========================

    edges = list(G.edges(data=True))

    edges.sort(
        key=lambda edge: edge[2].get("length", 0),
        reverse=True,
)

    print("\nTop 10 calles más largas\n")

    for edge in edges[:10]:
        print(f"{edge[2]['length']:.2f} m")


    # ==========================
    # Calles sin nombre
    # ==========================
    print("Calles sin nombre:")
    streets_without_name = 0

    for _, _, data in G.edges(data=True):

        if "name" not in data:
            streets_without_name += 1

    print(f"\nCalles sin nombre: {streets_without_name}")
    print(f"Porcentaje: {100 * streets_without_name / G.number_of_edges():.2f}%")


    degrees = dict(G.degree())

    top_nodes = sorted(
        degrees.items(),
        key=lambda x: x[1],
        reverse=True
    )
    print("\nTop 10 nodos más conectados\n")

    for node, degree in top_nodes[:10]:
        print(f"Nodo {node} -> {degree} conexiones")

    components = list(nx.connected_components(G.to_undirected()))
    print("\nConectividad")

    print(f"Componentes: {len(components)}")

    largest = max(components, key=len)

    print(f"Mayor componente: {len(largest)} nodos")

    xs = []
    ys = []

    for _, data in G.nodes(data=True):
        xs.append(data["x"])
        ys.append(data["y"])

    print("\nBounding Box")

    print(f"Latitud mínima : {min(ys)}")
    print(f"Latitud máxima : {max(ys)}")

    print(f"Longitud mínima : {min(xs)}")
    print(f"Longitud máxima : {max(xs)}")
    
    centroid_x = sum(xs) / len(xs)
    centroid_y = sum(ys) / len(ys)

    print("\nCentroide")

    print(f"Latitud : {centroid_y}")
    print(f"Longitud: {centroid_x}")

if __name__ == "__main__":
    analyze_graph()