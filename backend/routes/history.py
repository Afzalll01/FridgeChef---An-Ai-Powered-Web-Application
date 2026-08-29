from flask import Blueprint, request, jsonify
from database.db import db
from models.history import History

history_bp = Blueprint("history", __name__, url_prefix="/api")


@history_bp.route("/history", methods=["POST"])
def add_history():
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    search_term = (data.get("search_term") or "").strip()

    if not user_id or not search_term:
        return jsonify({"error": "Missing data"}), 400

    try:
        entry = History(user_id=int(user_id), search_term=search_term)
        db.session.add(entry)
        db.session.commit()
        return jsonify({"id": entry.id, "search_term": entry.search_term}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
