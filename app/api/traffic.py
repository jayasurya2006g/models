from fastapi import APIRouter, HTTPException
from app.schemas.schemas import TrajectoryRequest, TrafficRequest, ClusterRequest
from app.traffic.trajectory import analyze_trajectory
from app.traffic.analytics import analyze_traffic
from app.traffic.clustering import cluster_trajectories
from app.storage import latest_analysis, save_vehicles

router = APIRouter(prefix="/traffic", tags=["Traffic"])

@router.post("/trajectory")
def trajectory(req: TrajectoryRequest):
    try:
        save_vehicles([req])
        return {"success": True, **analyze_trajectory(req.vehicle_id, req.plate_number, req.points)}
    except Exception:
        import logging; logging.exception("Trajectory failed")
        raise HTTPException(500, "Trajectory analysis failed")

@router.post("/analyze")
def traffic(req: TrafficRequest):
    try:
        save_vehicles(req.vehicles)
        return {"success": True, **analyze_traffic(req.vehicles)}
    except Exception:
        import logging; logging.exception("Traffic analysis failed")
        raise HTTPException(500, "Traffic analysis failed")

@router.post("/cluster")
def cluster(req: ClusterRequest):
    try:
        save_vehicles(req.vehicles)
        return {"success": True, **cluster_trajectories(req.vehicles)}
    except Exception:
        import logging; logging.exception("Clustering failed")
        raise HTTPException(500, "Trajectory clustering failed")


@router.get("/live")
def live_traffic():
    analysis = latest_analysis()
    if analysis is None:
        return {"success": True, "updated_at": None, "message": "No traffic data received", "vehicles": []}
    return {"success": True, **analysis}
