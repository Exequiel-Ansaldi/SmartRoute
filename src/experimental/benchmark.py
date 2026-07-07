import random
import sys
import time
import tracemalloc
from pathlib import Path
import networkx as nx

from src.utils.load_graph import load_graph
from src.experimental.dijkstra import dijkstra_path_and_length
from src.experimental.astar import astar_shortest_path
from src.utils.load_graph import load_graph
from src.experimental.dijkstra import dijkstra_path_and_length
from src.experimental.astar import astar_shortest_path

def run_benchmark(num_queries=100, seed=42):
    print("Cargando grafo...")
    graph = load_graph()
    nodes = list(graph.nodes)
    
    # Seleccionar pares de nodos para consultas
    random.seed(seed)
    queries = []
    while len(queries) < num_queries:
        u = random.choice(nodes)
        v = random.choice(nodes)
        if u != v:
            queries.append((u, v))

    print(f"Ejecutando benchmark con {num_queries} consultas...")

    # 1. Custom Dijkstra
    tracemalloc.start()
    t0 = time.perf_counter()
    dijkstra_success = 0
    for u, v in queries:
        length, path = dijkstra_path_and_length(graph, u, v, weight="length")
        if length != float("inf"):
            dijkstra_success += 1
    t_dijkstra = time.perf_counter() - t0
    _, peak_dijkstra = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # 2. Custom A*
    tracemalloc.start()
    t0 = time.perf_counter()
    astar_success = 0
    for u, v in queries:
        length, path = astar_shortest_path(graph, u, v, weight="length")
        if length != float("inf"):
            astar_success += 1
    t_astar = time.perf_counter() - t0
    _, peak_astar = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # 3. NetworkX (shortest_path)
    tracemalloc.start()
    t0 = time.perf_counter()
    nx_success = 0
    for u, v in queries:
        try:
            # nx.bidirectional_shortest_path or standard shortest_path
            path = nx.shortest_path(graph, source=u, target=v, weight="length")
            nx_success += 1
        except nx.NetworkXNoPath:
            pass
    t_nx = time.perf_counter() - t0
    _, peak_nx = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print("\n--- RESULTADOS DEL BENCHMARK ---")
    print(f"Número de consultas: {num_queries}")
    print(f"Grafos conexos/rutas encontradas (Dijkstra/A*/NetworkX): {dijkstra_success}/{astar_success}/{nx_success}")
    print("-" * 75)
    print(f"{'Algoritmo':<20} | {'Tiempo Total (s)':<18} | {'Promedio/Consulta (ms)':<22} | {'Memoria Pico (KB)':<18}")
    print("-" * 75)
    print(f"{'Custom Dijkstra':<20} | {t_dijkstra:<18.4f} | {t_dijkstra * 1000 / num_queries:<22.4f} | {peak_dijkstra / 1024:<18.2f}")
    print(f"{'Custom A*':<20} | {t_astar:<18.4f} | {t_astar * 1000 / num_queries:<22.4f} | {peak_astar / 1024:<18.2f}")
    print(f"{'NetworkX (Dijkstra)':<20} | {t_nx:<18.4f} | {t_nx * 1000 / num_queries:<22.4f} | {peak_nx / 1024:<18.2f}")
    print("-" * 75)


if __name__ == "__main__":
    run_benchmark(num_queries=100)
