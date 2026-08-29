from flask import Blueprint, jsonify
from models.user import User
from services.auth_service import AuthService

users_bp = Blueprint("users", __name__, url_prefix="/api")


@users_bp.route("/user/<int:user_id>", methods=["GET"])
def get_user_profile(user_id: int):
    data, error, status_code = AuthService.get_user_profile_data(user_id)
    if error:
        return jsonify({"error": error}), status_code

    return jsonify(data), status_code


@users_bp.route("/test", methods=["GET"])
def test_users():
    try:
        count = User.query.count()
        return jsonify({"count": count}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
