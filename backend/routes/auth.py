from flask import Blueprint, request, jsonify
from services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__, url_prefix="/api")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    user_dict, error, status_code = AuthService.register_user(username, password, email)
    if error:
        return jsonify({"error": error}), status_code

    return jsonify(user_dict), status_code


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    user_dict, error, status_code = AuthService.authenticate_user(username, password)
    if error:
        return jsonify({"error": error}), status_code

    return jsonify(user_dict), status_code
