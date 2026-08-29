from flask import Blueprint, request, jsonify
from services.recipe_service import RecipeService, SpoonacularAPIError

recipes_bp = Blueprint("recipes", __name__, url_prefix="/api")


@recipes_bp.route("/recipes/search", methods=["GET"])
def search_recipes():
    ingredients = request.args.get("ingredients", "")
    number = request.args.get("number", default=9, type=int)

    if not ingredients:
        return jsonify([]), 200

    try:
        results = RecipeService.search_by_ingredients(ingredients, number=number)
        return jsonify(results), 200
    except SpoonacularAPIError as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500


@recipes_bp.route("/recipes/<int:recipe_id>", methods=["GET"])
@recipes_bp.route("/recipes/<int:recipe_id>/information", methods=["GET"])
def get_recipe(recipe_id: int):
    try:
        data = RecipeService.get_recipe_information(recipe_id)
        return jsonify(data), 200
    except SpoonacularAPIError as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

