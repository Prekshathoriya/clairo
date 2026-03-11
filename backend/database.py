import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "meetings.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            transcript TEXT NOT NULL,
            summary TEXT,
            action_items TEXT,
            decisions TEXT,
            speaker_stats TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_meeting(title: str, transcript: str, analysis: dict) -> int:
    conn = get_connection()
    cursor = conn.execute("""
        INSERT INTO meetings (title, transcript, summary, action_items, decisions, speaker_stats, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        title,
        transcript,
        analysis.get("summary", ""),
        json.dumps(analysis.get("action_items", [])),
        json.dumps(analysis.get("decisions", [])),
        json.dumps(analysis.get("speaker_stats", {})),
        datetime.now().isoformat()
    ))
    conn.commit()
    meeting_id = cursor.lastrowid
    conn.close()
    return meeting_id

def get_all_meetings():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM meetings ORDER BY created_at DESC").fetchall()
    conn.close()
    result = []
    for row in rows:
        result.append({
            "id": row["id"],
            "title": row["title"],
            "summary": row["summary"],
            "created_at": row["created_at"],
            "action_items": json.loads(row["action_items"] or "[]"),
            "decisions": json.loads(row["decisions"] or "[]"),
            "speaker_stats": json.loads(row["speaker_stats"] or "{}"),
        })
    return result

def get_meeting_by_id(meeting_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM meetings WHERE id = ?", (meeting_id,)).fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row["id"],
        "title": row["title"],
        "transcript": row["transcript"],
        "summary": row["summary"],
        "action_items": json.loads(row["action_items"] or "[]"),
        "decisions": json.loads(row["decisions"] or "[]"),
        "speaker_stats": json.loads(row["speaker_stats"] or "{}"),
        "created_at": row["created_at"],
    }

def delete_meeting(meeting_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM meetings WHERE id = ?", (meeting_id,))
    conn.commit()
    conn.close()
