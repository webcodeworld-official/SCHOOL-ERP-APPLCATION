import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATABASE = BASE_DIR / "school.db"

def get_connection():
    return sqlite3.connect(DATABASE)