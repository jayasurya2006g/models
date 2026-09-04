import os, re, logging
import cv2
import torch
from ultralytics import YOLO
from yolov5 import load as load_yolov5

os.environ.setdefault("TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD", "1")

class ANPREngine:
    def __init__(self):
        self.device = os.getenv("DEVICE", "cpu")
        self.vehicle_path = os.getenv("VEHICLE_MODEL_PATH", "weights/vehicle_model.pt")
        self.plate_path = os.getenv("PLATE_MODEL_PATH", "weights/plate_model.pt")
        # Lazy load models
        self.vehicle_model = None
        self.plate_model = None
        self.ocr = None
        self._models_loaded = False

    def _load_models(self):
        """Lazy load models on first use"""
        if self._models_loaded:
            return
        
        try:
            self.vehicle_model = YOLO(self.vehicle_path) if os.path.exists(self.vehicle_path) else None
            self.plate_model = load_yolov5(self.plate_path, device=self.device) if os.path.exists(self.plate_path) else None

            try:
                from paddleocr import PaddleOCR
                self.ocr = PaddleOCR(use_doc_orientation_classify=False,
                                     use_doc_unwarping=False,
                                     use_textline_orientation=False,
                                     enable_mkldnn=False,
                                     lang=os.getenv("OCR_LANG", "en"))
            except Exception as e:
                logging.warning("PaddleOCR unavailable: %s", e)
                self.ocr = None
            
            self._models_loaded = True
            logging.info("Models loaded successfully")
        except Exception as e:
            logging.error("Failed to load models: %s", e)
            raise

    def normalize(self, text):
        return re.sub(r"[^A-Z0-9]", "", text.upper())

    def ocr_plate(self, crop):
        if self.ocr is None or crop is None or crop.size == 0:
            return None, 0.0
        try:
            result = self.ocr.predict(crop)
            texts, scores = [], []
            for r in result:
                data = getattr(r, "json", None)
                if callable(data):
                    data = data()
                if isinstance(data, dict):
                    res = data.get("res", data)
                    texts += res.get("rec_texts", []) or []
                    scores += res.get("rec_scores", []) or []
            if not texts:
                return None, 0.0
            text = self.normalize("".join(map(str, texts)))
            score = float(sum(scores) / len(scores)) if scores else 0.0
            return text or None, score
        except Exception:
            logging.exception("OCR failed")
            return None, 0.0

    def process_image(self, image):
        # Lazy load models on first use
        self._load_models()
        
        if self.vehicle_model is None:
            raise RuntimeError("Vehicle model not found. Put it at weights/vehicle_model.pt")
        results = self.vehicle_model.predict(source=image, device=self.device, verbose=False)
        vehicles=[]
        for r in results:
            if r.boxes is None: continue
            names=r.names
            for box, conf, cls in zip(r.boxes.xyxy.cpu().numpy(),
                                      r.boxes.conf.cpu().numpy(),
                                      r.boxes.cls.cpu().numpy()):
                x1,y1,x2,y2=map(int, box)
                name=str(names[int(cls)]).lower()
                if name not in {"car","motorcycle","motorbike","bus","truck","vehicle"}:
                    continue
                item={"vehicle_model": name, "plate_number":None}
                if self.plate_model is not None:
                    crop=image[max(0,y1):min(image.shape[0],y2), max(0,x1):min(image.shape[1],x2)]
                    pres=self.plate_model(crop, size=640)
                    best=None
                    for detection in pres.pred[0].cpu().numpy():
                        pb, pc = detection[:4], detection[4]
                        if best is None or float(pc)>best[0]:
                            best=(float(pc), pb)
                    if best:
                        pc,pb=best
                        px1,py1,px2,py2=map(int,pb)
                        plate=crop[max(0,py1):min(crop.shape[0],py2),
                                   max(0,px1):min(crop.shape[1],px2)]
                        text,ocr_conf=self.ocr_plate(plate)
                        item["plate_number"]=text
                vehicles.append(item)
        return vehicles
