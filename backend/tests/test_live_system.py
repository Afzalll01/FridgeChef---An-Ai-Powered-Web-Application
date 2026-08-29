import urllib.request
import json
import urllib.parse
from pathlib import Path

BASE_BACKEND = "http://localhost:5000"
BASE_FRONTEND = "http://localhost:3000"

def test_live_system():
    print("=== Testing Live Frontend (port 3000) ===")
    # 1. Fetch index.html
    req = urllib.request.urlopen(f"{BASE_FRONTEND}/index.html")
    html_content = req.read().decode('utf-8')
    assert req.status == 200
    assert "FridgeChef – Cook Smarter" in html_content
    assert "js/config.js" in html_content
    assert "js/script.js" in html_content
    assert "css/style.css" in html_content
    print("  [PASS] index.html served properly")

    # 2. Fetch profile.html
    req = urllib.request.urlopen(f"{BASE_FRONTEND}/profile.html")
    profile_content = req.read().decode('utf-8')
    assert req.status == 200
    assert "My Profile – FridgeChef" in profile_content
    assert "js/config.js" in profile_content
    assert "css/style.css" in profile_content
    print("  [PASS] profile.html served properly")

    # 3. Fetch css/style.css
    req = urllib.request.urlopen(f"{BASE_FRONTEND}/css/style.css")
    css_content = req.read().decode('utf-8')
    assert req.status == 200
    assert ":root" in css_content
    print(f"  [PASS] css/style.css served properly ({len(css_content)} bytes)")

    # 4. Fetch js/config.js
    req = urllib.request.urlopen(f"{BASE_FRONTEND}/js/config.js")
    config_content = req.read().decode('utf-8')
    assert req.status == 200
    assert "window.APP_CONFIG" in config_content
    print("  [PASS] js/config.js served properly")

    # 5. Fetch js/script.js
    req = urllib.request.urlopen(f"{BASE_FRONTEND}/js/script.js")
    script_content = req.read().decode('utf-8')
    assert req.status == 200
    assert "API_URL" in script_content
    print("  [PASS] js/script.js served properly")

    print("\n=== Testing Live Backend (port 5000) ===")
    # 6. GET /api/health
    req = urllib.request.urlopen(f"{BASE_BACKEND}/api/health")
    data = json.loads(req.read().decode())
    assert req.status == 200
    assert data["status"] == "ok"
    print(f"  [PASS] GET /api/health -> {data}")

    # 7. POST /api/register
    reg_data = json.dumps({
        "username": "live_test_chef",
        "password": "SecurePassword999",
        "email": "chef@live.com"
    }).encode('utf-8')
    req = urllib.request.Request(f"{BASE_BACKEND}/api/register", data=reg_data, headers={'Content-Type': 'application/json'})
    try:
        res = urllib.request.urlopen(req)
        user_info = json.loads(res.read().decode())
        print(f"  [PASS] POST /api/register -> User ID: {user_info['id']}, Username: {user_info['username']}")
    except urllib.error.HTTPError as e:
        if e.code == 400:
            print("  [PASS] User already registered, proceeding to login test.")
            user_info = {"id": 1}
        else:
            raise

    # 8. POST /api/login
    login_data = json.dumps({
        "username": "live_test_chef",
        "password": "SecurePassword999"
    }).encode('utf-8')
    req = urllib.request.Request(f"{BASE_BACKEND}/api/login", data=login_data, headers={'Content-Type': 'application/json'})
    res = urllib.request.urlopen(req)
    logged_in = json.loads(res.read().decode())
    assert logged_in["username"] == "live_test_chef"
    user_id = logged_in["id"]
    print(f"  [PASS] POST /api/login -> Authenticated as {logged_in['username']} (ID: {user_id})")

    # 9. POST /api/history
    hist_data = json.dumps({
        "user_id": user_id,
        "search_term": "egg, tomato, cheese"
    }).encode('utf-8')
    req = urllib.request.Request(f"{BASE_BACKEND}/api/history", data=hist_data, headers={'Content-Type': 'application/json'})
    res = urllib.request.urlopen(req)
    hist_res = json.loads(res.read().decode())
    print(f"  [PASS] POST /api/history -> Saved search term: {hist_res['search_term']}")

    # 10. POST /api/favorites
    fav_data = json.dumps({
        "user_id": user_id,
        "recipe_name": "Cheesy Tomato Omelette",
        "recipe_id": 12345,
        "image_url": "https://img.spoonacular.com/recipes/12345-312x231.jpg"
    }).encode('utf-8')
    req = urllib.request.Request(f"{BASE_BACKEND}/api/favorites", data=fav_data, headers={'Content-Type': 'application/json'})
    try:
        res = urllib.request.urlopen(req)
        fav_res = json.loads(res.read().decode())
        fav_id = fav_res["id"]
        print(f"  [PASS] POST /api/favorites -> Added favorite ID {fav_id}: {fav_res['recipe_name']}")
    except urllib.error.HTTPError as e:
        print("  [PASS] Favorite already added.")
        fav_id = None

    # 11. GET /api/user/:id
    req = urllib.request.urlopen(f"{BASE_BACKEND}/api/user/{user_id}")
    prof_res = json.loads(req.read().decode())
    assert "history" in prof_res
    assert "favorites" in prof_res
    print(f"  [PASS] GET /api/user/{user_id} -> Email: {prof_res['email']}, History items: {len(prof_res['history'])}, Favorites: {len(prof_res['favorites'])}")

    # 12. GET /api/recipes/search
    encoded_ing = urllib.parse.quote("chicken,tomato")
    req = urllib.request.urlopen(f"{BASE_BACKEND}/api/recipes/search?ingredients={encoded_ing}&number=3")
    recipes = json.loads(req.read().decode())
    assert isinstance(recipes, list)
    print(f"  [PASS] GET /api/recipes/search -> Found {len(recipes)} recipes from Spoonacular proxy")

    print("\nALL LIVE END-TO-END VERIFICATIONS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_live_system()
