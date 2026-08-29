from .auth import auth_bp
from .users import users_bp
from .history import history_bp
from .favorites import favorites_bp
from .recipes import recipes_bp
from .detection import detection_bp
from .health import health_bp

__all__ = [
    "auth_bp",
    "users_bp",
    "history_bp",
    "favorites_bp",
    "recipes_bp",
    "detection_bp",
    "health_bp",
]
