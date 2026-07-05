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
