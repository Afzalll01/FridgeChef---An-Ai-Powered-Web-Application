from flask import Flask, request, jsonify
from flask_cors import CORS
from ultralytics import YOLO
import os

app = Flask(__name__)
CORS(app)

model = YOLO("models/fridge_yolov8.pt")

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return "FridgeChef AI Backend is running!"
@app.route('/detect', methods=['POST'])
def detect():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400

        file = request.files['image']
        image_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(image_path)

        results = model(image_path, conf=0.25)

        detected = []
        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                label = model.names[cls]
                if label not in detected:
                    detected.append(label)

        return jsonify({'ingredients': detected})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    app.run(debug=True)