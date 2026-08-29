import os
import logging
from flask import Blueprint, request, jsonify
from services.detection_service import DetectionService
from config import Config

logger = logging.getLogger(__name__)

detection_bp = Blueprint("detection", __name__)


@detection_bp.route("/api/detect", methods=["POST"])
@detection_bp.route("/detect", methods=["POST"])
def detect():
    logger.info("YOLO Detection request received at route handler.")
    try:
        if "image" not in request.files:
            logger.error("Request failed: 'image' form-data field not found in request.files.")
            return jsonify({"error": "No image uploaded"}), 400

        file = request.files["image"]
        if not file or not file.filename:
            logger.error("Request failed: Uploaded image file is empty or missing a filename.")
            return jsonify({"error": "Empty file uploaded"}), 400

        # Safe diagnostic logging of file properties
        try:
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            logger.info(f"Uploaded Image Info - Filename: '{file.filename}', Content Type: '{file.content_type}', File Size: {file_size} bytes")
        except Exception as fe:
            logger.warning(f"Could not safely read file size: {fe}")

        model_path = Config.MODEL_PATH
        model_exists = os.path.exists(model_path)
        logger.info(f"Model Configuration - Path: '{model_path}', File Exists: {model_exists}")

        detected_ingredients = DetectionService.detect_ingredients(file, conf_threshold=0.25)
        
        logger.info(f"Detection response successfully created. Detections count: {len(detected_ingredients)}")
        return jsonify({"ingredients": detected_ingredients}), 200

    except Exception as e:
        import traceback
        tb_str = traceback.format_exc()
        logger.error(f"Detection Route Exception Details:\nType: {type(e).__name__}\nMessage: {str(e)}\nTraceback:\n{tb_str}")
        return jsonify({"error": "Unable to process image"}), 500

