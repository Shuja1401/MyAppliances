import sqlite3
import os

def get_db():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "database", "database.db")

    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    print(f"[DEBUG] Using DB at: {db_path}")  # Optional for checking
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    return conn, c

def close_db(conn):
    conn.commit()
    conn.close()
