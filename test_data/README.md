# Standalone test data

These JSON files simulate the payloads that a future Node.js backend will send:

- `trajectory_single.json`: one vehicle with six geographic points.
- `traffic_multiple_vehicles.json`: ten vehicles, including eight moving and two stopped.
- `traffic_cluster.json`: fifteen vehicles in three intentional movement groups.
- `map_test.html`: a Leaflet page for visualizing and searching the multiple-vehicle fixture.
- `anpr/`: place real vehicle images here for manual ANPR uploads.

The fixtures are independent of FastAPI and can be removed when the Node.js
backend is ready. The API request schemas remain unchanged.
