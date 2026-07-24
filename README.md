-# FridgeChef - AI Powered Recipe Recommendation

FridgeChef is a web application that helps users find recipes using the ingredients available in their refrigerator. Users can either upload a fridge image or enter ingredients manually. The application uses a custom-trained YOLOv8 model to detect ingredients from images and then recommends suitable recipes.

## Features

- Detect ingredients from a fridge image
- Manual ingredient search
- Recipe recommendations
- Save favourite recipes
- View search history
- User profile page
- Dark mode

## Technologies Used

**Frontend**
- HTML
- CSS
- JavaScript

**Backend**
- Node.js
- Express.js
- Flask

**AI**
- YOLOv8 (Ultralytics)
- Python

## Project Structure

```
FridgeChef
│
├── app.py
├── server.js
├── package.json
├── index.html
├── profile.html
├── script.js
├── style.css
└── models/
    └── fridge_yolov8.pt
```

## How to Run

1. Clone the repository

```bash
git clone https://github.com/Afzalll01/FridgeChef---An-Ai-Powered-Web-Application.git
```

2. Install Node packages

```bash
npm install
```

3. Install Python packages

```bash
pip install flask ultralytics opencv-python
```

4. Start the Flask server

```bash
python app.py
```

5. Start the Node server

```bash
node server.js
```

Open the application in your browser.

## About the Model

The ingredient detection model was trained using YOLOv8 on a custom refrigerator ingredient dataset. The trained model is available in the `models` folder.

## Future Improvements

- Better recipe recommendations
- Nutrition information
- User login system
- Mobile-friendly interface

## Author

Afzal Nizami