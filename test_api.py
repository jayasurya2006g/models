"""Smoke-test the traffic API using the standalone JSON fixtures."""

import json
import os
from pathlib import Path

import requests


BASE_URL = os.getenv("TRAFFIC_API_URL", "http://127.0.0.1:8000")
ROOT = Path(__file__).parent


def load_fixture(name):
    with (ROOT / "test_data" / name).open(encoding="utf-8") as file:
        return json.load(file)


def post(path, payload):
    response = requests.post(f"{BASE_URL}{path}", json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def main():
    print("=" * 40)
    print("TRAFFIC AI API TEST")
    print("=" * 40)

    health = requests.get(f"{BASE_URL}/health", timeout=10)
    health.raise_for_status()
    assert health.json().get("success") is True
    print("\n[1] Health\nPASS")

    trajectory = post("/traffic/trajectory", load_fixture("trajectory_single.json"))
    assert trajectory["success"] and trajectory["movement_status"] == "MOVING"
    print("\n[2] Single Vehicle Trajectory\nPASS")
    print(f"Distance: {trajectory['total_distance_km']} km")
    print(f"Direction: {trajectory['direction']}")

    analysis = post("/traffic/analyze", load_fixture("traffic_multiple_vehicles.json"))
    assert analysis["success"] and analysis["total_vehicles"] == 10
    print("\n[3] Traffic Analysis\nPASS")
    print(f"Vehicles: {analysis['total_vehicles']}")
    print(f"Moving: {analysis['moving_vehicles']}")
    print(f"Stopped: {analysis['stopped_vehicles']}")
    print(f"Congestion: {analysis['congestion_level']}")

    clusters = post("/traffic/cluster", load_fixture("traffic_cluster.json"))
    assert clusters["success"] and len(clusters["clusters"]) >= 3
    print("\n[4] Trajectory Clustering\nPASS")
    print(f"Clusters found: {len(clusters['clusters'])}")

    print("\n" + "=" * 40)
    print("ALL TESTS COMPLETED")
    print("=" * 40)


if __name__ == "__main__":
    main()
