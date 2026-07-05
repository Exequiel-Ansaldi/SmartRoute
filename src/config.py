from pathlib import Path

SEED = 123

CLIENTS = 5

CITY = "Concordia, Entre Ríos, Argentina"
NETWORK_TYPE = "drive"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "raw"
GRAPH_FILENAME = "concordia.graphml"
GRAPH_PATH = DATA_DIR / GRAPH_FILENAME

ALLOWED_HIGHWAYS = {
    "residential",
    "secondary",
    "tertiary",
    "primary",
    "living_street",
    "unclassified",
}

DEFAULT_SPEED_KPH = 30.0
ASTAR_MAX_SPEED_KPH = 130.0

NUM_VEHICLES = 2
VEHICLE_CAPACITY = 10.0

ORTOOLS_TIME_LIMIT_SECONDS = 30
DEFAULT_SERVICE_TIME_SECONDS = 300.0
DEPOT_TIME_WINDOW = (0.0, 86400.0)

DEFAULT_SPEEDS_KPH = {
    "motorway": 110,
    "motorway_link": 60,
    "trunk": 100,
    "trunk_link": 50,
    "primary": 70,
    "primary_link": 40,
    "secondary": 60,
    "secondary_link": 35,
    "tertiary": 40,
    "tertiary_link": 30,
    "residential": 30,
    "living_street": 20,
    "unclassified": 30,
    "service": 20,
}
