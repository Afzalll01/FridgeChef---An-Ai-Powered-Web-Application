"""
Utility script to migrate existing SQLite records (users, history, favorites)
into the current Flask-SQLAlchemy database (PostgreSQL or new SQLite).
"""

import os
import sys
import sqlite3
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app import create_app
from database.db import db
from models.user import User
from models.history import History
from models.favorite import Favorite


def migrate(sqlite_source_path: str):
    if not os.path.exists(sqlite_source_path):
        print(f"[Error] Source SQLite file not found at: {sqlite_source_path}")
        return

    print(f"Connecting to source SQLite: {sqlite_source_path}...")
    src_conn = sqlite3.connect(sqlite_source_path)
    src_conn.row_factory = sqlite3.Row
    cursor = src_conn.cursor()

    app = create_app()
    with app.app_context():
        # Ensure destination tables exist
        db.create_all()

        # Migrate Users
        print("\n--- Migrating Users ---")
        try:
            cursor.execute("SELECT id, username, email, password FROM users")
            users = cursor.fetchall()
            for row in users:
                existing = User.query.filter_by(username=row["username"]).first()
                if not existing:
                    user = User(
                        id=row["id"],
                        username=row["username"],
                        email=row["email"]
                    )
                    # Use set_password or legacy pass
                    user.password = row["password"]  # Will auto-upgrade on login
                    db.session.add(user)
                    print(f"  + Added user: {row['username']} (ID: {row['id']})")
                else:
                    print(f"  - User already exists: {row['username']}")
            db.session.commit()
        except Exception as e:
            print(f"  [!] Users migration note: {e}")
            db.session.rollback()

        # Migrate History
        print("\n--- Migrating History ---")
        try:
            cursor.execute("SELECT id, user_id, search_term, created_at FROM history")
            history_rows = cursor.fetchall()
            for row in history_rows:
                existing = db.session.get(History, row["id"])
                if not existing:
                    h = History(
                        id=row["id"],
                        user_id=row["user_id"],
                        search_term=row["search_term"]
                    )
                    db.session.add(h)
            db.session.commit()
            print(f"  + Migrated {len(history_rows)} search history records.")
        except Exception as e:
            print(f"  [!] History migration note: {e}")
            db.session.rollback()

        # Migrate Favorites
        print("\n--- Migrating Favorites ---")
        try:
            cursor.execute("SELECT id, user_id, recipe_name, recipe_id, image_url, created_at FROM favorites")
            fav_rows = cursor.fetchall()
            for row in fav_rows:
                existing = db.session.get(Favorite, row["id"])
                if not existing:
                    f = Favorite(
                        id=row["id"],
                        user_id=row["user_id"],
                        recipe_name=row["recipe_name"],
                        recipe_id=row["recipe_id"],
                        image_url=row["image_url"]
                    )
                    db.session.add(f)
            db.session.commit()
            print(f"  + Migrated {len(fav_rows)} favorite recipes.")
        except Exception as e:
            print(f"  [!] Favorites migration note: {e}")
            db.session.rollback()

    src_conn.close()
    print("\nMigration completed successfully!")


if __name__ == "__main__":
    default_src = str(backend_dir.parent / "database.sqlite")
    source = sys.argv[1] if len(sys.argv) > 1 else default_src
    migrate(source)
