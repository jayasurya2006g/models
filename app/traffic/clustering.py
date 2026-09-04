import numpy as np
from sklearn.cluster import DBSCAN
from app.traffic.trajectory import hav

def cluster_trajectories(vehicles):
    if not vehicles:
        return {"clusters":[]}
    features=[]
    for v in vehicles:
        p=v.points
        features.append([p[0].lat,p[0].lng,p[-1].lat,p[-1].lng])
    labels=DBSCAN(eps=0.005, min_samples=2).fit_predict(np.array(features))
    clusters={}
    for v,label in zip(vehicles,labels):
        clusters.setdefault(int(label),[]).append(v.vehicle_id)
    return {"clusters":[{"cluster_id":k,"vehicle_ids":ids,"pattern":"NOISE" if k==-1 else "MOVEMENT_GROUP"}
                       for k,ids in clusters.items()]}
