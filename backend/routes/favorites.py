from flask import Blueprint, request, jsonify
from database.db import db
from models.favorite import Favorite

favorites_bp = Blueprint("favorites", __name__, url_prefix="/api")


@favorites_bp.route("/favorites", methods=["POST"])
def add_favorite():
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    recipe_name = (data.get("recipe_name") or "").strip()
    recipe_id = data.get("recipe_id")
    image_url = data.get("image_url")

    if not user_id or not recipe_name:
        return jsonify({"error": "Missing data"}), 400

    try:
        user_id_int = int(user_id)
        recipe_id_int = int(recipe_id) if recipe_id is not None else None

        # Check for existing favorite by same user
        existing = Favorite.query.filter_by(user_id=user_id_int, recipe_name=recipe_name).first()
        if existing:
            return jsonify({"error": "Recipe already in favorites"}), 400

        fav = Favorite(
            user_id=user_id_int,
            recipe_name=recipe_name,
            recipe_id=recipe_id_int,
            image_url=image_url
        )
        db.session.add(fav)
        db.session.commit()

        return jsonify({"id": fav.id, "recipe_name": fav.recipe_name}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@favorites_bp.route("/favorites/<int:favorite_id>", methods=["DELETE"])
def delete_favorite(favorite_id: int):
    user_id = request.args.get("user_id")

    if not favorite_id or not user_id:
        return jsonify({"error": "Missing data"}), 400

    try:
        user_id_int = int(user_id)
        fav = Favorite.query.filter_by(id=favorite_id, user_id=user_id_int).first()
        if not fav:
            return jsonify({"error": "Favorite not found"}), 404

        db.session.delete(fav)
        db.session.commit()
        return jsonify({"message": "Deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
