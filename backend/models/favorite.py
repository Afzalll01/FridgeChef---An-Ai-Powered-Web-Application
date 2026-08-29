from datetime import datetime, timezone
from database.db import db


class Favorite(db.Model):
    __tablename__ = "favorites"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    recipe_name = db.Column(db.String(255), nullable=False)
    recipe_id = db.Column(db.Integer, nullable=True)
    image_url = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        """Serialize favorite recipe to dictionary matching frontend expectations."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "recipe_name": self.recipe_name,
            "recipe_id": self.recipe_id,
            "image_url": self.image_url,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
