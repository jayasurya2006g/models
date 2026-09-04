import time
import cv2, numpy as np
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.models.anpr_engine import ANPREngine

router = APIRouter(prefix="/anpr", tags=["ANPR"])
engine = ANPREngine()

@router.post("/image")
async def anpr_image(
    file: UploadFile = File(...),
    timestamp: float | None = Form(None),
    camera_id: str | None = Form(None),
):
    detection_timestamp = timestamp if timestamp is not None else time.time()
    metadata = {"timestamp": detection_timestamp, "camera_id": camera_id}
    try:
        data = await file.read()
        image = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            raise HTTPException(400, "Invalid image")
        if engine.vehicle_model is None:
            return {"success": True, "vehicles": [], "message": "No vehicle detected", **metadata}
        vehicles = engine.process_image(image)
        for vehicle in vehicles:
            vehicle.update(metadata)
        return {"success": True, "vehicles": vehicles}
    except HTTPException:
        raise
    except RuntimeError as error:
        if str(error).startswith("Vehicle model not found"):
            return {"success": True, "vehicles": [], "message": "No vehicle detected", **metadata}
        import logging
        logging.exception("ANPR failed")
        raise HTTPException(500, "AI processing failed")
    except Exception:
        import logging
        logging.exception("ANPR failed")
        raise HTTPException(500, "AI processing failed")
