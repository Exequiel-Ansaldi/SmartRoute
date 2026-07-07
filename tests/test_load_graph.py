from src.utils import load_graph as load_graph_module


def test_load_graph_uses_cache(monkeypatch):
    calls = {"count": 0}
    fake_graph = object()

    def fake_load_graphml(path):
        calls["count"] += 1
        return fake_graph

    monkeypatch.setattr(load_graph_module.ox, "load_graphml", fake_load_graphml)

    if hasattr(load_graph_module.load_graph, "cache_clear"):
        load_graph_module.load_graph.cache_clear()

    first = load_graph_module.load_graph()
    second = load_graph_module.load_graph()

    assert first is fake_graph
    assert second is fake_graph
    assert calls["count"] == 1
