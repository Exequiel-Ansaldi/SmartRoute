from collections import defaultdict
from dataclasses import dataclass
import networkx as nx
from shapely.ops import substring
from typing import cast
from src.scenario.entities import Client, Depot, RoadPoint, Scenario


@dataclass(slots=True)
class AugmentationResult:
    graph: nx.MultiDiGraph
    inserted_nodes: list[str]
    removed_edges: list[tuple]
    added_edges: list[tuple]


class GraphAugmenter:
    """
    Clase responsable de transformar un grafo de OpenStreetMap (networkx.MultiDiGraph)
    en un grafo aumentado, insertando nuevos nodos que corresponden al depósito
    y a los clientes del escenario, dividiendo las aristas correspondientes.
    """

    def __init__(self, graph: nx.MultiDiGraph):
        self.graph = graph
        self._inserted_nodes = defaultdict(list)

    def augment(self, scenario: Scenario) -> AugmentationResult:
        """
        Transforma el grafo original en un grafo aumentado listo para
        ejecutar algoritmos de caminos mínimos.

        NUNCA modifica el grafo original. Trabaja sobre una copia.
        Devuelve un objeto AugmentationResult con el grafo obtenido y el
        registro de cambios realizados.
        """
        # Reiniciar el registro de nodos insertados para evitar fugas de estado entre llamadas
        self._inserted_nodes = defaultdict(list)

        # Crear una copia del grafo para no modificar el original
        augmented_graph = cast(nx.MultiDiGraph, self.graph.copy())

        # Insertar el depósito
        self._insert_point(augmented_graph, scenario.depot, "depot")

        # Insertar los clientes
        for client in scenario.clients:
            self._insert_point(augmented_graph, client, "client")

        # Determinar de forma exacta los cambios realizados comparando ambos grafos
        is_multi = self.graph.is_multigraph()
        
        original_nodes_set = set(self.graph.nodes)
        augmented_nodes_set = set(augmented_graph.nodes)
        inserted_nodes = list(augmented_nodes_set - original_nodes_set)

        original_edges_set = set(self.graph.edges(keys=is_multi))
        augmented_edges_set = set(augmented_graph.edges(keys=is_multi))
        
        removed_edges = list(original_edges_set - augmented_edges_set)
        added_edges = list(augmented_edges_set - original_edges_set)

        return AugmentationResult(
            graph=augmented_graph,
            inserted_nodes=inserted_nodes,
            removed_edges=removed_edges,
            added_edges=added_edges,
        )

    def _insert_point(self, graph: nx.MultiDiGraph, road_point: Client | Depot, kind: str) -> None:
        """
        Inserta un RoadPoint (depósito o cliente) en el grafo de forma incremental.

        Si ya existen nodos previamente insertados en la misma arista original,
        los ordena para insertar el nuevo punto en el segmento correcto, manteniendo
        la consistencia geométrica y las distancias.
        """
        u = road_point.node_u
        v = road_point.node_v
        new_node_id = road_point.id
        new_dist = road_point.distance_to_u
        new_fraction = road_point.edge_fraction

        # Determinar cuál es la arista original correspondiente en el grafo original (self.graph).
        # Esto es necesario para conservar atributos de calle (highway, name, etc.) y la geometría original.
        target_length = road_point.distance_to_u + road_point.distance_to_v
        
        if self.graph.is_multigraph():
            edge_dict = self.graph[u][v]
            best_key = None
            min_diff = float("inf")
            for k, data in edge_dict.items():
                length = data.get("length", 0)
                diff = abs(length - target_length)
                if diff < min_diff:
                    min_diff = diff
                    best_key = k
            if best_key is None:
                best_key = list(edge_dict.keys())[0]
            key = best_key
            original_edge_data = edge_dict[key]
        else:
            key = None
            original_edge_data = self.graph[u][v]

        original_length = original_edge_data.get("length", target_length)
        original_geometry = original_edge_data.get("geometry")

        # Obtener los nodos previamente insertados en esta arista original
        existing = self._inserted_nodes[(u, v, key)]

        # Agregar el nuevo nodo al grafo con sus atributos correspondientes
        graph.add_node(
            new_node_id,
            x=road_point.longitude,
            y=road_point.latitude,
            kind=kind
        )

        if not existing:
            # Caso 1: Es el primer punto insertado en esta arista. Eliminamos la original (u, v).
            if graph.is_multigraph():
                graph.remove_edge(u, v, key=key)
            else:
                graph.remove_edge(u, v)

            # Construir datos para el segmento inicial (u, new_node)
            data_u = original_edge_data.copy()
            data_u["length"] = road_point.distance_to_u
            if original_geometry is not None:
                try:
                    data_u["geometry"] = substring(
                        original_geometry, 0, new_fraction, normalized=True
                    )
                except Exception:
                    data_u.pop("geometry", None)

            # Construir datos para el segmento final (new_node, v)
            data_v = original_edge_data.copy()
            data_v["length"] = road_point.distance_to_v
            if original_geometry is not None:
                try:
                    data_v["geometry"] = substring(
                        original_geometry, new_fraction, 1.0, normalized=True
                    )
                except Exception:
                    data_v.pop("geometry", None)

            # Añadir las nuevas aristas
            if graph.is_multigraph():
                graph.add_edge(u, new_node_id, key=key, **data_u)
                graph.add_edge(new_node_id, v, key=key, **data_v)
            else:
                graph.add_edge(u, new_node_id, **data_u)
                graph.add_edge(new_node_id, v, **data_v)

            # Registrar la inserción actual
            self._inserted_nodes[(u, v, key)].append((new_node_id, new_dist, new_fraction))
        else:
            # Caso 2: Ya existen otros puntos en esta arista.
            # Ordenamos todos los puntos de la arista (incluido el nuevo) por su distancia a 'u'.
            all_insertions = sorted(
                existing + [(new_node_id, new_dist, new_fraction)],
                key=lambda x: x[1]
            )

            # Encontrar la posición del nuevo punto en la lista ordenada
            idx = -1
            for i, (node_id, _, _) in enumerate(all_insertions):
                if node_id == new_node_id:
                    idx = i
                    break

            # Determinar los nodos fronterizos (anterior y posterior) del nuevo punto
            if idx == 0:
                prev_node = u
                prev_dist = 0.0
                prev_fraction = 0.0
            else:
                prev_node, prev_dist, prev_fraction = all_insertions[idx - 1]

            if idx == len(all_insertions) - 1:
                next_node = v
                next_dist = original_length
                next_fraction = 1.0
            else:
                next_node, next_dist, next_fraction = all_insertions[idx + 1]

            # Eliminar la arista intermedia existente entre prev_node y next_node
            if graph.is_multigraph():
                graph.remove_edge(prev_node, next_node, key=key)
            else:
                graph.remove_edge(prev_node, next_node)

            # Construir datos para el segmento izquierdo (prev_node, new_node)
            data_u = original_edge_data.copy()
            data_u["length"] = max(0.0, new_dist - prev_dist)
            if original_geometry is not None:
                try:
                    data_u["geometry"] = substring(
                        original_geometry, prev_fraction, new_fraction, normalized=True
                    )
                except Exception:
                    data_u.pop("geometry", None)

            # Construir datos para el segmento derecho (new_node, next_node)
            data_v = original_edge_data.copy()
            data_v["length"] = max(0.0, next_dist - new_dist)
            if original_geometry is not None:
                try:
                    data_v["geometry"] = substring(
                        original_geometry, new_fraction, next_fraction, normalized=True
                    )
                except Exception:
                    data_v.pop("geometry", None)

            # Añadir las nuevas aristas
            if graph.is_multigraph():
                graph.add_edge(prev_node, new_node_id, key=key, **data_u)
                graph.add_edge(new_node_id, next_node, key=key, **data_v)
            else:
                graph.add_edge(prev_node, new_node_id, **data_u)
                graph.add_edge(new_node_id, next_node, **data_v)

            # Registrar la inserción actual
            self._inserted_nodes[(u, v, key)].append((new_node_id, new_dist, new_fraction))
