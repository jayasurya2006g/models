from math import radians, sin, cos, sqrt, atan2, degrees

def hav(a,b):
    R=6371.0088
    p1,p2=radians(a.lat),radians(b.lat)
    dp=radians(b.lat-a.lat); dl=radians(b.lng-a.lng)
    x=sin(dp/2)**2+cos(p1)*cos(p2)*sin(dl/2)**2
    return 2*R*atan2(sqrt(x),sqrt(1-x))

def analyze_trajectory(vehicle_id, plate_number, points):
    total=0.0; speeds=[]; bearings=[]
    for a,b in zip(points,points[1:]):
        d=hav(a,b); total+=d
        if a.timestamp is not None and b.timestamp is not None and b.timestamp>a.timestamp:
            speeds.append(d/((b.timestamp-a.timestamp)/3600))
        bearings.append((degrees(atan2(
            sin(radians(b.lng-a.lng))*cos(radians(b.lat)),
            cos(radians(a.lat))*sin(radians(b.lat))-sin(radians(a.lat))*cos(radians(b.lat))*cos(radians(b.lng-a.lng))
        ))+360)%360)
    avg=sum(speeds)/len(speeds) if speeds else None
    direction=None
    if bearings:
        x=sum(cos(radians(v)) for v in bearings); y=sum(sin(radians(v)) for v in bearings)
        angle=(degrees(atan2(y,x))+360)%360
        direction=["N","NE","E","SE","S","SW","W","NW"][int((angle+22.5)//45)%8]
    duration=(points[-1].timestamp-points[0].timestamp) if points[0].timestamp is not None and points[-1].timestamp is not None else None
    return {"vehicle_id":vehicle_id,"plate_number":plate_number,
            "total_distance_km":round(total,5),
            "average_speed_kmh":round(avg,3) if avg is not None else None,
            "direction":direction,
            "movement_status":"MOVING" if total>0.005 else "STOPPED",
            "duration_seconds":duration,
            "trajectory":[p.model_dump() for p in points]}
