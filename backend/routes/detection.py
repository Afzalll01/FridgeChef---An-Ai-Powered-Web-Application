import logging
from flask import Blueprint, request, jsonify
from services.detection_service import DetectionService

logger = logging.getLogger(__name__)

detection_bp = Blueprint("detection", __name__)


@detection_bp.route("/api/detect", methods=["POST"])
@detection_bp.route("/detect", methods=["POST"])
def detect():
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image uploaded"}), 400

        file = request.files["image"]
        if not file or not file.filename:
            return jsonify({"error": "Empty file uploaded"}), 400

        detected_ingredients = DetectionService.detect_ingredients(file, conf_threshold=0.25)
        return jsonify({"ingredients": detected_ingredients}), 200

    except Exception as e:
        logger.exception(f"Error during fridge image detection: {e}")
        return jsonify({"error": str(e)}), 500
