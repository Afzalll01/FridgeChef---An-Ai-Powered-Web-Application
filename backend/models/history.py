from datetime import datetime, timezone
from database.db import db


class History(db.Model):
    __tablename__ = "history"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    search_term = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        """Serialize history item to dictionary matching frontend expectations."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "search_term": self.search_term,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
