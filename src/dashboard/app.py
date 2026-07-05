from pathlib import Path
from tempfile import TemporaryDirectory

import streamlit as st

from main import run_pipeline
from src.config import CLIENTS, NUM_VEHICLES, SEED, VEHICLE_CAPACITY


st.set_page_config(page_title="Optimización de Rutas", layout="wide")

st.title("Optimización de Rutas")

with st.sidebar:
    clients = st.number_input("Clientes", min_value=1, max_value=100, value=CLIENTS)
    seed = st.number_input("Seed", min_value=0, value=SEED)
    algorithm = st.selectbox("Algoritmo", ["vrp", "tsp"])
    vehicles = st.number_input(
        "Vehículos", min_value=1, max_value=50, value=NUM_VEHICLES
    )
    capacity = st.number_input(
        "Capacidad", min_value=1.0, value=float(VEHICLE_CAPACITY)
    )
    run = st.button("Ejecutar")

if run:
    with st.spinner("Calculando rutas..."):
        with TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "routes.png"
            result = run_pipeline(
                clients=int(clients),
                seed=int(seed),
                vehicles=int(vehicles),
                capacity=float(capacity),
                algorithm=algorithm,
                output=output,
                show_plot=False,
            )

            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Rutas", len(result.routes))
            col_b.metric("Nodos", len(result.nodes))
            col_c.metric("Tiempo simulado", f"{result.simulation.total_time:.0f} s")

            st.image(str(output), use_container_width=True)

            st.subheader("Rutas")
            for route in result.routes:
                st.write(
                    f"Vehículo {route.vehicle_id}: "
                    f"{' -> '.join(route.route)} "
                    f"(costo {route.total_cost:.2f}, carga {route.load:.2f})"
                )

            if result.solution is not None and result.solution.unassigned:
                st.warning(
                    "Clientes sin asignar: "
                    + ", ".join(result.solution.unassigned)
                )

            st.subheader("Eventos")
            st.dataframe(
                [
                    {
                        "vehiculo": event.vehicle_id,
                        "tipo": event.event_type,
                        "nodo": event.node_id,
                        "inicio": event.start_time,
                        "fin": event.end_time,
                        "descripcion": event.description,
                    }
                    for event in result.simulation.events
                ],
                use_container_width=True,
            )
else:
    st.info("Elegí parámetros y ejecutá la simulación.")

