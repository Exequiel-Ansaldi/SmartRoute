def reconstruct_node_path(
    visit_order: list[str], paths: dict[str, dict[str, list]]
) -> list[str | int]:
    """
    Traduce una secuencia optimizada de visitas al camino real de nodos del grafo.
    """
    full_path: list[str | int] = []

    for origin, destination in zip(visit_order, visit_order[1:]):
        segment = paths.get(origin, {}).get(destination, [])
        if not segment:
            raise ValueError(f"No hay camino guardado entre {origin} y {destination}.")

        if full_path:
            full_path.extend(segment[1:])
        else:
            full_path.extend(segment)

    return full_path


def reconstruct_edge_path(
    visit_order: list[str], paths: dict[str, dict[str, list]]
) -> list[tuple[str | int, str | int]]:
    """
    Traduce una secuencia optimizada de visitas a aristas consecutivas del grafo.
    """
    node_path = reconstruct_node_path(visit_order, paths)
    return list(zip(node_path, node_path[1:]))
