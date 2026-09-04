from pydantic import BaseModel, Field
from typing import Optional, List

class Point(BaseModel):
    lat: float
    lng: float
    timestamp: Optional[float] = None
    camera_id: Optional[str] = None

class TrajectoryRequest(BaseModel):
    vehicle_id: str
    plate_number: Optional[str] = None
    points: List[Point] = Field(min_length=1)

class VehicleTrajectory(BaseModel):
    vehicle_id: str
    plate_number: Optional[str] = None
    points: List[Point] = Field(min_length=1)

class TrafficRequest(BaseModel):
    vehicles: List[VehicleTrajectory]

class ClusterRequest(BaseModel):
    vehicles: List[VehicleTrajectory]
    eps_km: float = 0.5
    min_samples: int = 2
