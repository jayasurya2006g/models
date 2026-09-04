import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.anpr import router as anpr_router
from app.api.traffic import router as traffic_router
from app.storage import init_db, recent_vehicles, save_analysis
from app.traffic.analytics import analyze_traffic
from app.schemas.schemas import VehicleTrajectory


async def analysis_worker():
    while True:
        vehicles = [VehicleTrajectory.model_validate(vehicle) for vehicle in recent_vehicles()]
        if vehicles:
            save_analysis(analyze_traffic(vehicles))
        await asyncio.sleep(10)


@asynccontextmanager
async def lifespan(_app):
    init_db()
    worker = asyncio.create_task(analysis_worker())
    try:
        yield
    finally:
        worker.cancel()
        await asyncio.gather(worker, return_exceptions=True)


app = FastAPI(title="Traffic AI Service", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(anpr_router)
app.include_router(traffic_router)

@app.get("/health")
def health():
    return {"success": True, "service": "traffic-ai", "status": "ok"}
