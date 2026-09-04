from app.traffic.trajectory import analyze_trajectory

def analyze_traffic(vehicles):
    analyses=[analyze_trajectory(v.vehicle_id,v.plate_number,v.points) for v in vehicles]
    speeds=[a["average_speed_kmh"] for a in analyses if a["average_speed_kmh"] is not None]
    moving=sum(a["movement_status"]=="MOVING" for a in analyses)
    stopped=len(analyses)-moving
    avg=sum(speeds)/len(speeds) if speeds else None
    stop_ratio=stopped/len(analyses) if analyses else 0
    if stop_ratio>=.6 or (avg is not None and avg<10): level="SEVERE"
    elif stop_ratio>=.4 or (avg is not None and avg<20): level="HIGH"
    elif stop_ratio>=.2 or (avg is not None and avg<30): level="MEDIUM"
    else: level="LOW"
    return {"total_vehicles":len(analyses),"moving_vehicles":moving,
            "stopped_vehicles":stopped,"average_speed_kmh":round(avg,3) if avg is not None else None,
            "congestion_level":level,"vehicles":analyses}
