import logging
from database.db import db
from models.user import User
from models.history import History
from models.favorite import Favorite

logger = logging.getLogger(__name__)


class AuthService:
    @staticmethod
    def register_user(username: str, password: str, email: str = None) -> tuple[dict | None, str | None, int]:
        """
        Register a new user.
        Returns: (user_dict, error_message, http_status_code)
        """
        username = (username or "").strip()
        password = (password or "").strip()
        email = (email or "").strip() or None

        if not username or not password:
            return None, "Username and password are required", 400

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return None, "Username already exists", 400

        try:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return user.to_dict(), None, 201
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error registering user {username}: {e}")
            return None, "Database error during registration", 500

    @staticmethod
    def authenticate_user(username: str, password: str) -> tuple[dict | None, str | None, int]:
        """
        Authenticate an existing user.
        Returns: (user_dict, error_message, http_status_code)
        """
        username = (username or "").strip()
        password = (password or "").strip()

        if not username or not password:
            return None, "Username and password are required", 400

        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return None, "Invalid credentials", 401

        return user.to_dict(), None, 200

    @staticmethod
    def get_user_profile_data(user_id: int) -> tuple[dict | None, str | None, int]:
        """
        Fetch full profile data (email, top 20 history items, all favorites).
        Returns exact dictionary structure expected by existing profile.html frontend.
        """
        user = db.session.get(User, user_id)
        if not user:
            return None, "User not found", 404

        try:
            # Query top 20 search history ordered by created_at DESC
            history_rows = (
                History.query.filter_by(user_id=user_id)
                .order_by(History.created_at.desc())
                .limit(20)
                .all()
            )

            # Query favorites ordered by created_at DESC
            favorites_rows = (
                Favorite.query.filter_by(user_id=user_id)
                .order_by(Favorite.created_at.desc())
                .all()
            )

            response_data = {
                "email": user.email,
                "history": [h.to_dict() for h in history_rows],
                "favorites": [f.to_dict() for f in favorites_rows]
            }

            return response_data, None, 200
        except Exception as e:
            logger.error(f"Error loading profile for user {user_id}: {e}")
            return None, str(e), 500


# Expose functions at the module level for direct imports
register_user = AuthService.register_user
authenticate_user = AuthService.authenticate_user
get_user_profile_data = AuthService.get_user_profile_data

