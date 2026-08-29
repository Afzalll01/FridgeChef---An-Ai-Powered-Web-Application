import sys
import os
import requests
from pathlib import Path

def test_detect():
    test_png = Path(__file__).resolve().parent.parent.parent / "test.png"
    print(f"Test image path: {test_png}")
    print(f"Exists: {test_png.exists()}")

    url = "http://localhost:5000/api/detect"
    print(f"Sending POST to {url}...")

    with open(test_png, "rb") as f:
        files = {"image": ("test.png", f, "image/png")}
        try:
            r = requests.post(url, files=files, timeout=30)
            print(f"Status: {r.status_code}")
            print(f"Response: {r.text}")
        except Exception as e:
            print(f"Failed: {e}")

if __name__ == "__main__":
    test_detect()
