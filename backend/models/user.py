from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), nullable=True)
    password = db.Column(db.String(255), nullable=False)

    # Relationships
    history_entries = db.relationship("History", backref="user", lazy=True, cascade="all, delete-orphan")
    favorite_recipes = db.relationship("Favorite", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, raw_password: str):
        """Hash and set user password securely."""
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """
        Verify password against stored hash.
        Includes automatic legacy plain-text fallback and upgrade.
        """
        if not self.password:
            return False

        # If stored as Werkzeug hash
        try:
            if check_password_hash(self.password, raw_password):
                return True
        except Exception:
            pass

        # Legacy plain-text fallback check for pre-refactor records
        if self.password == raw_password:
            # Upgrade legacy plaintext to secure hash automatically
            self.set_password(raw_password)
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
            return True

        return False

    def to_dict(self):
        """Return user dict for API response."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email
        }
