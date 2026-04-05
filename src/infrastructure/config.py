import os

_BASE = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(_BASE))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATABASE_PATH = os.path.join(DATA_DIR, "database.db")
BACKUPS_DIR = os.path.join(DATA_DIR, "backups")
