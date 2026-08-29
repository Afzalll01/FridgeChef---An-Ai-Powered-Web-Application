import logging
import requests
from config import Config

logger = logging.getLogger(__name__)

SPOONACULAR_BASE_URL = "https://api.spoonacular.com/recipes"


class SpoonacularAPIError(Exception):
    """Exception raised when Spoonacular API requests fail."""
    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.status_code = status_code


class RecipeService:
    @staticmethod
    def search_by_ingredients(ingredients: list[str] | str, number: int = 9) -> list[dict]:
        """
        Search Spoonacular recipes based on comma-separated or list of ingredients.
        """
        if isinstance(ingredients, list):
            ingredients_str = ",".join([i.strip() for i in ingredients if i.strip()])
        else:
            ingredients_str = str(ingredients).strip()

        if not ingredients_str:
            return []

        api_key = Config.SPOONACULAR_API_KEY
        url = f"{SPOONACULAR_BASE_URL}/findByIngredients"
        params = {
            "ingredients": ingredients_str,
            "number": number,
            "apiKey": api_key
        }

        logger.info(f"Querying Spoonacular API: {url} with ingredients='{ingredients_str}'")

        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                logger.info(f"Spoonacular API returned 200 OK with {len(response.json())} recipes.")
                return response.json()
            else:
                err_msg = f"Spoonacular API returned non-200 status {response.status_code}: {response.text}"
                logger.error(err_msg)
                raise SpoonacularAPIError(
                    message=f"Spoonacular API Error: {response.reason or 'Error'} ({response.status_code})",
                    status_code=response.status_code
                )
        except requests.RequestException as e:
            err_msg = f"Network/HTTP error querying Spoonacular API: {e}"
            logger.error(err_msg)
            raise SpoonacularAPIError(message=f"Network error communicating with recipe provider: {e}", status_code=502)

    @staticmethod
    def get_recipe_information(recipe_id: int) -> dict:
        """
        Fetch detailed recipe information (ingredients, instructions, nutrition) from Spoonacular.
        """
        api_key = Config.SPOONACULAR_API_KEY
        url = f"{SPOONACULAR_BASE_URL}/{recipe_id}/information"
        params = {
            "apiKey": api_key
        }

        logger.info(f"Querying Spoonacular API for recipe details: {url}")

        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                logger.info(f"Spoonacular API returned 200 OK for recipe details of ID {recipe_id}.")
                return response.json()
            else:
                err_msg = f"Spoonacular API returned non-200 status {response.status_code} for recipe details of ID {recipe_id}: {response.text}"
                logger.error(err_msg)
                raise SpoonacularAPIError(
                    message=f"Spoonacular API Error: {response.reason or 'Error'} ({response.status_code})",
                    status_code=response.status_code
                )
        except requests.RequestException as e:
            err_msg = f"Network/HTTP error querying Spoonacular API details: {e}"
            logger.error(err_msg)
            raise SpoonacularAPIError(message=f"Network error communicating with recipe provider: {e}", status_code=502)


# Expose functions at the module level for direct imports
search_by_ingredients = RecipeService.search_by_ingredients
get_recipe_information = RecipeService.get_recipe_information


