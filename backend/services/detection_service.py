import os
import tempfile
import uuid
import logging
import time
import torch
from PIL import Image, ImageOps
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
            
            logger.info(f"YOLO Initialization - Checking model path: '{model_path}'")
            if not os.path.exists(model_path):
                logger.error(f"YOLO Initialization Failed: Model file not found at: '{model_path}'")
                raise FileNotFoundError(f"YOLO model file not found at: {model_path}")

            logger.info(f"YOLO Initialization - Loading weights from: '{model_path}'")
            load_start = time.time()
            cls._model = YOLO(model_path)
            load_duration = time.time() - load_start
            logger.info(f"YOLO Initialization Complete - Loaded weights in {load_duration:.4f}s. Class names: {cls._model.names}")
        
        return cls._model

    @classmethod
    def detect_ingredients(cls, file_storage, conf_threshold: float = 0.25) -> list[str]:
        """
        Run YOLOv8 inference on uploaded image file.
        Safely saves to a temporary file and cleans it up after inference.
        Returns a list of unique detected ingredient names.
        """
        logger.info("Entering detect_ingredients service method.")
        start_time = time.time()
        
        # Load the cached model
        model = cls.get_model()

        # Generate unique temporary file name (standardized to JPEG suffix)
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, f"fridge_{uuid.uuid4().hex}.jpg")
        
        logger.info(f"Temporary image save target: '{temp_file_path}'")

        try:
            # Safely read, rotate, and downscale image before saving
            logger.info("Loading image stream via Pillow for preprocessing...")
            file_storage.seek(0)
            img = Image.open(file_storage.stream)
            img = ImageOps.exif_transpose(img)
            
            orig_w, orig_h = img.size
            logger.info(f"Original image resolution: {orig_w}x{orig_h}")
            
            # Resize if the longest side exceeds 800px
            if max(orig_w, orig_h) > 800:
                img.thumbnail((800, 800), Image.Resampling.LANCZOS)
                logger.info(f"Resized image to: {img.width}x{img.height}")
            
            # Convert RGBA/LA to RGB if necessary for JPEG compatibility
            if img.mode in ('RGBA', 'LA'):
                img = img.convert('RGB')

            # Save the optimized image to the temporary file path
            img.save(temp_file_path, format="JPEG", quality=85)
            temp_file_exists = os.path.exists(temp_file_path)
            temp_file_size = os.path.getsize(temp_file_path) if temp_file_exists else 0
            logger.info(f"Optimized temporary image saved: '{temp_file_path}' (Size: {temp_file_size} bytes)")

            # Run inference under inference_mode
            logger.info("Initiating YOLO inference run on CPU...")
            inference_start = time.time()
            
            with torch.inference_mode():
                # Restrict to CPU explicitly, set standard image size to 640
                results = model(temp_file_path, conf=conf_threshold, device='cpu', imgsz=640)
            
            inference_duration = time.time() - inference_start
            logger.info(f"YOLO inference run completed in {inference_duration:.4f} seconds.")

            detected = []
            box_count = 0
            for r in results:
                box_count += len(r.boxes)
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    label = model.names[cls_id]
                    clean_label = label.lower().strip()
                    if clean_label and clean_label not in detected:
                        detected.append(clean_label)

            total_duration = time.time() - start_time
            logger.info(f"Detection Success - Total request time: {total_duration:.4f}s. Frames: {len(results)}, Boxes: {box_count}, Detected ingredients: {detected}")
            return detected

        except Exception as e:
            logger.error(f"Exception during YOLO inference pipeline: {e}")
            raise
        finally:
            # Safely clean up temporary file
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    logger.info(f"Successfully cleaned up temporary file: '{temp_file_path}'")
                except Exception as err:
                    logger.warning(f"Failed to remove temp file {temp_file_path}: {err}")


# Expose functions at the module level for direct imports
detect_ingredients = DetectionService.detect_ingredients
