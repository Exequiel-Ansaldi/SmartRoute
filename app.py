from pathlib import Path

import streamlit as st

from main import run_pipeline
from src.utils.load_graph import load_graph

st.set_page_config(page_title="Optimizador de Rutas", page_icon="🚗", layout="wide")

st.title("🚗 Optimización de rutas en Concordia")
st.markdown("Seleccioná los parámetros y observá cómo cambian las rutas, los vehículos y el mapa.")


@st.cache_resource
def get_graph():
    return load_graph()


@st.cache_data(show_spinner=False)
def run_cached_pipeline(
    clients: int,
    seed: int,
    vehicles: int,
    algorithm: str,
    output: str,
    animation_output: str,
) -> dict:
    result = run_pipeline(
        clients=clients,
        seed=seed,
        vehicles=vehicles,
        algorithm=algorithm,
        output=output,
        animation_output=animation_output,
        show_plot=False,
    )
    return {
        "nodes": result.nodes,
        "routes": result.routes,
        "solution": result.solution,
        "total_time": result.simulation.total_time,
        "bottlenecks": len(result.simulation.bottlenecks),
    }

with st.sidebar:
    st.header("Parámetros")
    clients = st.slider("Clientes", min_value=1, max_value=15, value=6)
    vehicles = st.slider("Vehículos", min_value=1, max_value=4, value=2)

    if "manual_algorithm" not in st.session_state:
        st.session_state.manual_algorithm = "vrp"

    if vehicles > 1:
        st.session_state.manual_algorithm = "vrp"

    manual_algorithm = st.selectbox(
        "Algoritmo",
        options=["tsp", "vrp"],
        format_func=lambda value: "TSP" if value == "tsp" else "VRP",
        index=["tsp", "vrp"].index(st.session_state.manual_algorithm),
        disabled=vehicles > 1,
    )

    if vehicles <= 1:
        st.session_state.manual_algorithm = manual_algorithm

    effective_algorithm = "vrp" if vehicles > 1 else st.session_state.manual_algorithm
    st.info(f"Algoritmo activo: {effective_algorithm.upper()}")

    seed = st.number_input("Semilla", min_value=0, max_value=1000, value=123)
    show_animation = st.checkbox("Generar animación", value=True)
    run_button = st.button("Ejecutar simulación", use_container_width=True)

if run_button:
    get_graph()

    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    static_path = str(output_dir / "dashboard_routes.png")
    animation_path = str(output_dir / "dashboard_routes.gif")

    with st.spinner("Generando escenario y calculando rutas..."):
        cached = run_cached_pipeline(
            clients=clients,
            seed=seed,
            vehicles=vehicles,
            algorithm=effective_algorithm,
            output=static_path,
            animation_output=animation_path if show_animation else "",
        )

    st.success("Simulación lista")

    col1, col2, col3 = st.columns(3)
    col1.metric("Algoritmo", effective_algorithm.upper())
    col2.metric("Clientes", len(cached["nodes"]) - 1)
    col3.metric("Tiempo total", f"{cached['total_time']:.2f} s")

    anim_path = Path(animation_path)
    if show_animation and anim_path.exists():
        st.subheader("Animación")
        st.image(str(anim_path), use_container_width=True)

    st.subheader("Detalle")
    for route in cached["routes"]:
        st.write(f"Vehículo {route.vehicle_id}: {' -> '.join(route.route)} | costo {route.total_cost:.2f}")
else:
    st.info("Presioná ejecutar para generar una nueva simulación.")
