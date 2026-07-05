# Roadmap Consolidado: Optimización de Rutas

Este documento unifica tu roadmap original con mis sugerencias técnicas para lograr un sistema de optimización de rutas robusto, escalable y visualmente impactante.

```mermaid
graph TD
    A[Fase 1: Grafo y Escenarios] -->|Grafo Aumentado| B[Fase 2: Caminos Mínimos]
    B -->|Matriz de Distancias| C[Fase 3: Optimización]
    C -->|Secuencia de Visitas| D[Fase 4: Simulación y Visualización]
    D -->|Motor de Rutas| E[Fase 5: Dashboard e Interfaz]
    E -->|Aplicación Completa| F[Fase 6: Productivización]
```

---

## 📋 Estado del Proyecto y Próximos Pasos

### 🔹 Fase 1: Base Geográfica y Generación de Escenarios (Completado)
* [x] **Descarga de Ciudad (OSMnx)**: Descarga y almacenamiento de Concordia en formato `.graphml` ([download_city.py](file:///c:/Users/GAMER/PROYECCTO_OPTIMIZACION_RUTS/src/download/download_city.py)).
* [x] **EDA (Análisis Exploratorio de Datos)**: Análisis estadístico de calles, sentidos y conectividad ([graph_analysis.py](file:///c:/Users/GAMER/PROYECCTO_OPTIMIZACION_RUTS/src/analysis/graph_analysis.py)).
* [x] **Configuración**: Parámetros globales y tipos de calles válidas ([config.py](file:///c:/Users/GAMER/PROYECCTO_OPTIMIZACION_RUTS/src/config.py)).
* [x] **Entidades**: Modelado de datos en [entities.py](file:///c:/Users/GAMER/PROYECCTO_OPTIMIZACION_RUTS/src/scenario/entities.py).
* [x] **ScenarioGenerator**: Generación reproducible de clientes y depósitos sobre las aristas ([generator.py](file:///c:/Users/GAMER/PROYECCTO_OPTIMIZACION_RUTS/src/scenario/generator.py)).
* [x] **GraphAugmenter**: Inserción geométrica óptima de clientes en el grafo vial sin alterar el original ([augment_graph.py](file:///c:/Users/GAMER/PROYECCTO_OPTIMIZACION_RUTS/src/graph/augment_graph.py)).

### ⬜ Fase 2: Validación y Robustez del Grafo Aumentado
* [ ] **Validación del Grafo Aumentado**:
  * [ ] **Visualización**: Robustecer [graph_plotter.py](file:///c:/Users/GAMER/PROYECCTO_OPTIMIZACION_RUTS/src/visualization/graph_plotter.py) para que visualice correctamente inserciones complejas (varios clientes en una misma cuadra).
  * [ ] **Tests Unitarios**: Extender [test_augment_graph.py](file:///c:/Users/GAMER/PROYECCTO_OPTIMIZACION_RUTS/tests/test_augment_graph.py) cubriendo casos borde (depósito y cliente en la misma arista, coordenadas idénticas, calles de un solo sentido).

### 🔹 Fase 3: Caminos Mínimos y Matriz de Costos (Completado)
* [x] **Dijkstra Custom vs. NetworkX**:
  * [x] Implementación propia de Dijkstra punto-a-punto adaptada a las aristas del grafo aumentado ([dijkstra.py](file:///C:/Users/GAMER/PROYECCTO_OPTIMIZACION_RUTS/src/routing/dijkstra.py)).
  * [x] **Benchmark**: Evaluar el tiempo de ejecución y uso de memoria de nuestra implementación vs `nx.shortest_path_length` en grafos grandes ([benchmark.py](file:///C:/Users/GAMER/PROYECCTO_OPTIMIZACION_RUTS/src/routing/benchmark.py)).
* [x] **A* (A-Estrella)**:
  * [x] Implementar A* con una función heurística basada en la distancia de Haversine (usando las coordenadas de latitud/longitud de los nodos) para acelerar consultas individuales ([astar.py](file:///C:/Users/GAMER/PROYECCTO_OPTIMIZACION_RUTS/src/routing/astar.py)).
* [x] **Generador de Matriz de Distancias (y Tiempos)**:
  * [x] Crear una clase `CostMatrixGenerator` que calcule las distancias mínimas en un formato matricial de $N \times N$ (donde $N = \text{clientes} + \text{depósito}$) ([matrix.py](file:///C:/Users/GAMER/PROYECCTO_OPTIMIZACION_RUTS/src/routing/matrix.py)).
  * [x] Agregar cálculo de tiempos estimados de viaje según el tipo de calle (`maxspeed`).


### ⬜ Fase 4: Algoritmos de Optimización de Rutas
* [ ] **TSP (Travelling Salesperson Problem)**:
  * [ ] Solución óptima o heurística (Nearest Neighbor + Búsqueda Local 2-Opt) para un único vehículo.
* [ ] **VRP (Vehicle Routing Problem)**:
  * [ ] Extender el problema a múltiples vehículos considerando capacidades de carga (`CVRP`) y, opcionalmente, ventanas de tiempo (`VRPTW`).
  * [ ] Integración de resolvedor matemático como **Google OR-Tools** o implementaciones metaheurísticas.
* [ ] **Reconstrucción del Camino Geométrico**:
  * [ ] Traducir el orden óptimo de clientes de vuelta a una lista ordenada de aristas del grafo vial para poder trazar el camino exacto calle por calle.

### ⬜ Fase 5: Simulación Logística y Visualización
* [ ] **Visualización de Recorridos**:
  * [ ] Graficar las rutas resultantes diferenciando cada vehículo con colores llamativos y flechas de sentido sobre el mapa de Concordia.
* [ ] **Simulación Logística**:
  * [ ] Crear un simulador temporal que muestre el avance de los vehículos en tiempo real, calculando el momento de llegada a cada cliente e identificando posibles cuellos de botella (por ejemplo, congestión simulada).

### ⬜ Fase 6: Interfaz y Despliegue (Productivización)
* [ ] **Script Runner Principal (`main.py`)**:
  * [ ] Archivo de entrada interactivo para correr simulaciones desde la terminal.
* [ ] **Dashboard Interactivo**:
  * [ ] Desarrollar una aplicación web ligera (por ejemplo, con **Streamlit** o **Dash**) que permita elegir la cantidad de clientes, posicionar el depósito con un clic, ejecutar la optimización y ver los mapas interactivos (`folium` / `ipyleaflet`).
* [ ] **Documentación**:
  * [ ] Agregar Guía de Arquitectura, API docs y manual de usuario.
* [ ] **Docker & Infraestructura**:
  * [ ] Crear un `Dockerfile` optimizado para empaquetar las dependencias geoespaciales (`GDAL`, `PROJ`, etc.) que suelen dar problemas de instalación.
* [ ] **CI/CD**:
  * [ ] Pipeline en GitHub Actions para validación automática de formato (`black`/`flake8`), chequeo de tipos (`mypy`) y ejecución automática de tests en cada push.
