from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200


@health_bp.route("/", methods=["GET"])
def home():
    return "FridgeChef AI Backend is running!", 200
