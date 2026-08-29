import os
import tempfile
import uuid
import logging
from ultralytics import YOLO
from config import Config

logger = logging.getLogger(__name__)


class DetectionService:
    _model = None

    @classmethod
    def get_model(cls):
        """Lazy-load and cache the YOLO model singleton."""
        if cls._model is None:
            model_path = Config.MODEL_PATH
            if not os.path.isabs(model_path):
                model_path = os.path.abspath(model_path)
            
            if not os.path.exists(model_path):
                logger.error(f"YOLO model file not found at: {model_path}")
                raise FileNotFoundError(f"YOLO model file not found at: {model_path}")

            logger.info(f"Loading YOLO model from: {model_path}")
            cls._model = YOLO(model_path)
            logger.info(f"YOLO model loaded successfully with {len(cls._model.names)} classes.")
        
        return cls._model

    @classmethod
    def detect_ingredients(cls, file_storage, conf_threshold: float = 0.25) -> list[str]:
        """
        Run YOLOv8 inference on uploaded image file.
        Safely saves to a temporary file and cleans it up after inference.
        Returns a list of unique detected ingredient names.
        """
        model = cls.get_model()

        # Generate unique temporary file name
        suffix = os.path.splitext(file_storage.filename or "image.jpg")[1] or ".jpg"
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, f"fridge_{uuid.uuid4().hex}{suffix}")

        try:
            # Save file to temporary path
            file_storage.save(temp_file_path)

            # Run inference
            results = model(temp_file_path, conf=conf_threshold)

            detected = []
            for r in results:
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    label = model.names[cls_id]
                    clean_label = label.lower().strip()
                    if clean_label and clean_label not in detected:
                        detected.append(clean_label)

            return detected

        finally:
            # Safely clean up temporary file
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except Exception as err:
                    logger.warning(f"Failed to remove temp file {temp_file_path}: {err}")


# Expose functions at the module level for direct imports
detect_ingredients = DetectionService.detect_ingredients

