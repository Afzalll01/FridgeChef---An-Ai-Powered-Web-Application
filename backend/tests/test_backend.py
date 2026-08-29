import os
import sys
import unittest
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app import create_app
from database.db import db
from models.user import User
from models.history import History
from models.favorite import Favorite


class BackendTestCase(unittest.TestCase):
    def setUp(self):
        # Configure app with in-memory SQLite database for testing
        class TestConfig:
            TESTING = True
            SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
            SQLALCHEMY_TRACK_MODIFICATIONS = False
            SECRET_KEY = "test-secret"
            ALLOWED_ORIGINS = ["*"]
            UPLOAD_FOLDER = str(backend_dir / "uploads")
            MODEL_PATH = str(backend_dir / "models_ai" / "fridge_yolov8.pt")
            SPOONACULAR_API_KEY = "f27dfecc2f80481bb246959ef390881b"
            PORT = 5000
            DEBUG = False

        self.app = create_app(TestConfig)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_health_check(self):
        """Test GET /api/health endpoint."""
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json(), {"status": "ok"})

    def test_root_route(self):
        """Test GET / endpoint."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"FridgeChef AI Backend is running!", res.data)

    def test_registration_and_login_flow(self):
        """Test registration, hashing, legacy plain upgrade, and login verification."""
        # 1. Register new user
        reg_res = self.client.post("/api/register", json={
            "username": "chef_john",
            "password": "SecretPassword123",
            "email": "john@example.com"
        })
        self.assertEqual(reg_res.status_code, 201)
        reg_data = reg_res.get_json()
        self.assertEqual(reg_data["username"], "chef_john")
        self.assertEqual(reg_data["email"], "john@example.com")
        user_id = reg_data["id"]

        # Verify password is NOT stored as plaintext in DB
        with self.app.app_context():
            db_user = db.session.get(User, user_id)
            self.assertNotEqual(db_user.password, "SecretPassword123")
            self.assertTrue(db_user.password.startswith("scrypt:") or db_user.password.startswith("pbkdf2:"))

        # 2. Login with valid credentials
        login_res = self.client.post("/api/login", json={
            "username": "chef_john",
            "password": "SecretPassword123"
        })
        self.assertEqual(login_res.status_code, 200)
        self.assertEqual(login_res.get_json()["id"], user_id)

        # 3. Login with invalid password
        bad_login = self.client.post("/api/login", json={
            "username": "chef_john",
            "password": "WrongPassword"
        })
        self.assertEqual(bad_login.status_code, 401)

        # 4. Duplicate username check
        dup_res = self.client.post("/api/register", json={
            "username": "chef_john",
            "password": "AnotherPassword"
        })
        self.assertEqual(dup_res.status_code, 400)

        # 5. Test legacy plaintext password auto-upgrade
        with self.app.app_context():
            legacy_user = User(username="legacy_user", email="legacy@example.com", password="legacy_plain_password")
            db.session.add(legacy_user)
            db.session.commit()
            legacy_id = legacy_user.id

        legacy_login = self.client.post("/api/login", json={
            "username": "legacy_user",
            "password": "legacy_plain_password"
        })
        self.assertEqual(legacy_login.status_code, 200)

        # Check that it upgraded to hash in DB
        with self.app.app_context():
            upgraded_user = db.session.get(User, legacy_id)
            self.assertNotEqual(upgraded_user.password, "legacy_plain_password")

    def test_history_and_favorites_and_profile(self):
        """Test search history recording, adding/deleting favorites, and profile aggregation."""
        # Create user
        reg_res = self.client.post("/api/register", json={
            "username": "sarah",
            "password": "password123",
            "email": "sarah@example.com"
        })
        user_id = reg_res.get_json()["id"]

        # Add Search History
        hist_res = self.client.post("/api/history", json={
            "user_id": user_id,
            "search_term": "chicken, garlic, pasta"
        })
        self.assertEqual(hist_res.status_code, 201)
        self.assertEqual(hist_res.get_json()["search_term"], "chicken, garlic, pasta")

        # Add Favorite
        fav_res = self.client.post("/api/favorites", json={
            "user_id": user_id,
            "recipe_name": "Garlic Chicken Pasta",
            "recipe_id": 644387,
            "image_url": "https://img.spoonacular.com/recipes/644387-312x231.jpg"
        })
        self.assertEqual(fav_res.status_code, 201)
        fav_id = fav_res.get_json()["id"]

        # Duplicate Favorite check
        dup_fav = self.client.post("/api/favorites", json={
            "user_id": user_id,
            "recipe_name": "Garlic Chicken Pasta"
        })
        self.assertEqual(dup_fav.status_code, 400)

        # Get User Profile
        prof_res = self.client.get(f"/api/user/{user_id}")
        self.assertEqual(prof_res.status_code, 200)
        prof_data = prof_res.get_json()
        self.assertEqual(prof_data["email"], "sarah@example.com")
        self.assertEqual(len(prof_data["history"]), 1)
        self.assertEqual(prof_data["history"][0]["search_term"], "chicken, garlic, pasta")
        self.assertEqual(len(prof_data["favorites"]), 1)
        self.assertEqual(prof_data["favorites"][0]["recipe_name"], "Garlic Chicken Pasta")

        # Delete Favorite
        del_res = self.client.delete(f"/api/favorites/{fav_id}?user_id={user_id}")
        self.assertEqual(del_res.status_code, 200)
        self.assertEqual(del_res.get_json(), {"message": "Deleted"})

        # Check profile again - favorites should be empty
        prof_res2 = self.client.get(f"/api/user/{user_id}")
        self.assertEqual(len(prof_res2.get_json()["favorites"]), 0)

    def test_yolo_detection_endpoint(self):
        """Test YOLO fridge detection endpoint with test image."""
        test_img_path = Path(__file__).resolve().parent.parent.parent / "test.png"
        if not test_img_path.exists():
            self.skipTest("test.png not found")

        with open(test_img_path, "rb") as img_file:
            res = self.client.post(
                "/api/detect",
                data={"image": (img_file, "test.png")},
                content_type="multipart/form-data"
            )
            self.assertEqual(res.status_code, 200)
            data = res.get_json()
            self.assertIn("ingredients", data)
            self.assertIsInstance(data["ingredients"], list)
            print(f"YOLO detected ingredients from test.png: {data['ingredients']}")

        # Backwards compatible route check
        with open(test_img_path, "rb") as img_file:
            res_bc = self.client.post(
                "/detect",
                data={"image": (img_file, "test.png")},
                content_type="multipart/form-data"
            )
            self.assertEqual(res_bc.status_code, 200)

    def test_recipe_routes(self):
        """Test recipe search and details route endpoints."""
        search_res = self.client.get("/api/recipes/search?ingredients=chicken,tomato&number=3")
        self.assertEqual(search_res.status_code, 200)
        search_data = search_res.get_json()
        self.assertIsInstance(search_data, list)


if __name__ == "__main__":
    unittest.main()
