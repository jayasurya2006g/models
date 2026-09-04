from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.anpr import router as anpr_router


app = FastAPI(title="ANPR Detection Service", version="1.0.0", description="License Plate Detection and OCR Service")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(anpr_router)

@app.get("/health")
def health():
    return {"success": True, "service": "anpr-detection", "status": "ok"}
