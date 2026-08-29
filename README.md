# FridgeChef — AI-Powered Recipe Recommendation Web Application

[![Backend: Python Flask](https://img.shields.io/badge/Backend-Python%20Flask-blue.svg)](https://flask.palletsprojects.com/)
[![Database: PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791.svg)](https://www.postgresql.org/)
[![AI: YOLOv8](https://img.shields.io/badge/AI-Ultralytics%20YOLOv8-FF6F00.svg)](https://docs.ultralytics.com/)
[![Frontend: Vercel](https://img.shields.io/badge/Frontend-Vercel-black.svg)](https://vercel.com/)
[![Backend: Render](https://img.shields.io/badge/Deploy-Render-46E3B7.svg)](https://render.com/)

**FridgeChef** is an AI-powered web application that helps users discover delicious recipes using the ingredients currently available in their refrigerator. Users can either scan an image of their fridge using a custom-trained **YOLOv8** object detection model or manually select ingredients. The application recommends recipes, provides detailed cooking instructions, and allows users to manage search history and favorite recipes in their profile.

---

## 🌟 Key Features

- 📸 **AI Fridge Scanner**: Upload a fridge photo to automatically detect ingredients using custom-trained YOLOv8.
- 🛒 **Smart Ingredient Search**: Autocomplete search bar and quick-add chips for fast ingredient entry.
- 🍽️ **Recipe Discovery & Details**: View recommended recipes, match percentages, ingredient breakdowns, and cooking instructions.
- 👤 **User Authentication**: Secure user registration and login with encrypted password hashing.
- ⭐ **Favorites & History**: Save favorite recipes and review recent ingredient searches directly in your profile dashboard.
- 🌙 **Dark Mode**: Seamless theme switching with user preference persistence.

---

## 🏗️ System Architecture

```
                                  ┌───────────────────────────┐
                                  │      Vercel Frontend      │
                                  │ (HTML5, Vanilla CSS, JS)  │
                                  └─────────────┬─────────────┘
                                                │ REST API / JSON
                                                ▼
                                  ┌───────────────────────────┐
                                  │       Render Backend      │
                                  │    (Python Flask + WSGI)  │
                                  └──────┬─────────────┬──────┘
                                         │             │
                    ┌────────────────────┴──┐       ┌──┴────────────────────┐
                    │  PostgreSQL Database  │       │ YOLOv8 Model Service  │
                    │  (Users, Favs, Hist)  │       │  (fridge_yolov8.pt)   │
                    └───────────────────────┘       └───────────────────────┘
```

- **Frontend**: Lightweight, high-performance static client deployed to **Vercel**.
- **Backend**: Unified **Python Flask** backend organized with modular Blueprints, deployed to **Render**.
- **Database**: **PostgreSQL** managed via **SQLAlchemy** ORM (with local SQLite fallback for development).
- **AI/Vision**: Custom **YOLOv8** object detection model (`backend/models_ai/fridge_yolov8.pt`).

---

## 📁 Project Structure

```
FridgeChef/
├── frontend/
│   ├── index.html            # Main discovery & search dashboard
│   ├── profile.html          # User profile, favorites & history page
│   ├── css/
│   │   └── style.css         # Design system & responsive styles
│   ├── js/
│   │   ├── config.js         # Dynamic environment & backend API configuration
│   │   └── script.js         # Frontend controller, search, AI, and modal logic
│   └── vercel.json           # Vercel deployment & routing configuration
│
├── backend/
│   ├── app.py                # Flask application factory and entry point
│   ├── config.py             # Environment configuration & settings
│   ├── requirements.txt      # Python dependencies
│   ├── runtime.txt           # Python runtime version for cloud deployments
│   ├── .env.example          # Environment variables template
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── db.py             # SQLAlchemy instance initialization
│   │   └── migrate_sqlite.py # Legacy SQLite to PostgreSQL migration script
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py           # User model with Werkzeug password hashing
│   │   ├── history.py        # Search history model
│   │   └── favorite.py       # Favorite recipe model
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py           # POST /api/register, POST /api/login
│   │   ├── users.py          # GET /api/user/<id>, GET /api/test
│   │   ├── history.py        # POST /api/history
│   │   ├── favorites.py      # POST /api/favorites, DELETE /api/favorites/<id>
│   │   ├── recipes.py        # GET /api/recipes/search, GET /api/recipes/<id>
│   │   ├── detection.py      # POST /api/detect (YOLO inference)
│   │   └── health.py         # GET /api/health
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py      # User authentication & profile business logic
│   │   ├── recipe_service.py    # Spoonacular API client & recipe parsing
│   │   └── detection_service.py # YOLO model singleton & image inference
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py        # Response helpers and utilities
│   │
│   ├── models_ai/
│   │   └── fridge_yolov8.pt  # Custom-trained YOLOv8 model weights
│   │
│   └── tests/
│       └── test_backend.py   # Automated unit and API integration tests
│
├── .gitignore
└── README.md
```

---

## 🚀 Local Development Setup

### 1. Prerequisites
- Python 3.10+ installed
- Git

### 2. Backend Setup
1. Navigate to the `backend/` directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create `.env` file from `.env.example`:
   ```bash
   cp .env.example .env
   ```
5. Run the Flask server:
   ```bash
   python app.py
   ```
   The backend will start at `http://localhost:5000`.

### 3. Frontend Setup
You can serve the `frontend/` directory using any static web server (such as Python's `http.server`, VS Code Live Server, or `npx serve`):
```bash
# From workspace root
python -m http.server 3000 --directory frontend
```
Open `http://localhost:3000` in your web browser.

---

## 🧪 Running Automated Tests

To run the automated backend test suite:
```bash
python backend/tests/test_backend.py
```

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service health check |
| `POST` | `/api/register` | Register new user `{ username, password, email? }` |
| `POST` | `/api/login` | Authenticate user `{ username, password }` |
| `GET` | `/api/user/<id>` | Fetch user profile, search history, and favorites |
| `POST` | `/api/history` | Record search history `{ user_id, search_term }` |
| `POST` | `/api/favorites` | Add favorite recipe `{ user_id, recipe_name, recipe_id, image_url }` |
| `DELETE` | `/api/favorites/<id>?user_id=<user_id>` | Remove favorite recipe |
| `POST` | `/api/detect` | Upload fridge image for YOLO ingredient detection |
| `GET` | `/api/recipes/search?ingredients=...` | Search recipes by ingredients |
| `GET` | `/api/recipes/<recipe_id>` | Get recipe details and instructions |

---

## 🌐 Production Deployment

### 1. Database (Render PostgreSQL)
1. In Render Dashboard, click **New +** → **PostgreSQL**.
2. Name your database (e.g. `fridgechef-db`).
3. Copy the **Internal Database URL** (or External Database URL).

### 2. Backend (Render Web Service)
1. In Render Dashboard, click **New +** → **Web Service**.
2. Connect your GitHub repository.
3. Configure the service settings:
   - **Root Directory**: `backend`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120`
4. Add Environment Variables:
   - `DATABASE_URL`: Your PostgreSQL connection string
   - `SECRET_KEY`: A secure random string
   - `SPOONACULAR_API_KEY`: Your Spoonacular API key
   - `FRONTEND_URL`: `https://your-app.vercel.app`

### 3. Frontend (Vercel)
1. Import your GitHub repository into **Vercel**.
2. Set **Root Directory** to `frontend`.
3. In `frontend/js/config.js`, update `DEFAULT_PROD_API` to point to your Render backend URL (e.g., `https://your-backend.onrender.com/api`).
4. Click **Deploy**.

---

## 👨‍💻 Author
**Afzal Nizami**