import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from database.db import db
from routes.auth import auth_bp
from routes.users import users_bp
from routes.history import history_bp
from routes.favorites import favorites_bp
from routes.recipes import recipes_bp
from routes.detection import detection_bp
from routes.health import health_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("fridgechef")


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize CORS
    # In development, allows localhost origins. In production, allows Vercel domain from FRONTEND_URL.
    CORS(
        app,
        resources={r"/*": {"origins": app.config["ALLOWED_ORIGINS"] or "*"}},
        supports_credentials=True
    )

    # Initialize SQLAlchemy database
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(favorites_bp)
    app.register_blueprint(recipes_bp)
    app.register_blueprint(detection_bp)

    # Ensure tables exist
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables initialized successfully.")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")

    # Global Error Handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "An internal server error occurred"}), 500

    return app


app = create_app()

if __name__ == "__main__":
    port = Config.PORT
    debug = Config.DEBUG
    logger.info(f"Starting FridgeChef Backend on port {port} (debug={debug})")
    app.run(host="0.0.0.0", port=port, debug=debug)
