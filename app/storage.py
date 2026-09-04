import json
import os
import sqlite3
import time
from pathlib import Path


DATABASE_PATH = Path(os.getenv("TRAFFIC_DB_PATH", "data/traffic.db"))


def _connect():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH, timeout=30)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with _connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id TEXT NOT NULL,
                plate_number TEXT,
                lat REAL,
                lng REAL,
                timestamp REAL NOT NULL,
                camera_id TEXT,
                vehicle_type TEXT,
                vehicle_confidence REAL,
                plate_confidence REAL,
                vehicle_bbox TEXT,
                plate_bbox TEXT,
                created_at REAL NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_detections_timestamp
                ON detections(timestamp);
            CREATE TABLE IF NOT EXISTS analysis_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at REAL NOT NULL,
                summary TEXT NOT NULL
            );
            """
        )


def save_vehicles(vehicles):
    now = time.time()
    rows = []
    for vehicle in vehicles:
        vehicle_data = vehicle if isinstance(vehicle, dict) else vehicle.model_dump()
        for point in vehicle_data["points"]:
            if point.get("timestamp") is None:
                continue
            rows.append(
                (
                    vehicle_data["vehicle_id"],
                    vehicle_data.get("plate_number"),
                    point.get("lat"),
                    point.get("lng"),
                    point["timestamp"],
                    point.get("camera_id"),
                    None,
                    None,
                    None,
                    None,
                    None,
                    now,
                )
            )
    if not rows:
        return
    with _connect() as connection:
        connection.executemany(
            """
            INSERT INTO detections (
                vehicle_id, plate_number, lat, lng, timestamp, camera_id,
                vehicle_type, vehicle_confidence, plate_confidence,
                vehicle_bbox, plate_bbox, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )


def save_anpr_detections(vehicles, timestamp, camera_id, lat=None, lng=None, vehicle_id=None):
    detection_time = timestamp if timestamp is not None else time.time()
    rows = []
    for index, vehicle in enumerate(vehicles):
        rows.append(
            (
                vehicle_id or vehicle.get("plate_number") or f"ANPR_{int(detection_time)}_{index + 1}",
                vehicle.get("plate_number"),
                lat,
                lng,
                detection_time,
                camera_id,
                vehicle.get("vehicle_type"),
                vehicle.get("vehicle_confidence"),
                vehicle.get("plate_confidence"),
                json.dumps(vehicle.get("vehicle_bbox")),
                json.dumps(vehicle.get("plate_bbox")),
                time.time(),
            )
        )
    if not rows:
        return
    with _connect() as connection:
        connection.executemany(
            """
            INSERT INTO detections (
                vehicle_id, plate_number, lat, lng, timestamp, camera_id,
                vehicle_type, vehicle_confidence, plate_confidence,
                vehicle_bbox, plate_bbox, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )


def recent_vehicles(window_seconds=60):
    cutoff = time.time() - window_seconds
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT vehicle_id, plate_number, lat, lng, timestamp, camera_id
            FROM detections
            WHERE timestamp >= ? AND lat IS NOT NULL AND lng IS NOT NULL
            ORDER BY vehicle_id, timestamp, id
            """,
            (cutoff,),
        ).fetchall()
    grouped = {}
    for row in rows:
        grouped.setdefault(
            row["vehicle_id"],
            {"vehicle_id": row["vehicle_id"], "plate_number": row["plate_number"], "points": []},
        )["points"].append(
            {
                "lat": row["lat"],
                "lng": row["lng"],
                "timestamp": row["timestamp"],
                "camera_id": row["camera_id"],
            }
        )
    return list(grouped.values())


def save_analysis(summary):
    with _connect() as connection:
        connection.execute(
            "INSERT INTO analysis_runs (created_at, summary) VALUES (?, ?)",
            (time.time(), json.dumps(summary),),
        )


def latest_analysis():
    with _connect() as connection:
        row = connection.execute(
            "SELECT created_at, summary FROM analysis_runs ORDER BY id DESC LIMIT 1"
        ).fetchone()
    if row is None:
        return None
    return {"updated_at": row["created_at"], **json.loads(row["summary"])}