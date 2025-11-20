# gate/ext/db.py

import sqlite3

from models import TrackEvent

# Create persistent in-memory DB connection
conn = sqlite3.connect(":memory:", check_same_thread=False)
cursor = conn.cursor()

# Initialize DB schema
def init_db():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event TEXT,
        agent TEXT,
        action TEXT,
        timestamp REAL,
        success INTEGER,
        created_at TEXT
    );
    """)
    conn.commit()


init_db()


# Insert event
def insert_event(e: TrackEvent):
    cursor.execute("""
        INSERT INTO events (event, agent, action, timestamp, success, created_at)
        VALUES (?, ?, ?, ?, ?, datetime('now'))
    """, (
        e["event"],
        e["agent"],
        e["action"],
        e["timestamp"],
        1 if e.get("success") else 0 if e.get("success") is not None else None
    ))
    conn.commit()


# Fetch events
def list_events(limit: int = 200):
    cursor.execute("""
        SELECT id, event, agent, action, timestamp, success, created_at
        FROM events
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    return cursor.fetchall()
