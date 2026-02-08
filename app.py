from flask import Flask, render_template, request, jsonify
import os
import json
import base64
from datetime import datetime
import pytz

app = Flask(__name__)

HISTORY_FILE = "history.json"
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/scan")
def scan():
    return render_template("scan.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/history")
def history():
    if not os.path.exists(HISTORY_FILE):
        history_data = []
    else:
        try:
            with open(HISTORY_FILE, "r") as f:
                history_data = json.load(f)
                if not isinstance(history_data, list):
                    history_data = []
        except:
            history_data = []

    return render_template("history.html", history=history_data)

def save_history(is_cancer, confidence, image_filename):
    try:
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
    except:
        history = []

    thai_tz = pytz.timezone("Asia/Bangkok")
    now = datetime.now(thai_tz)

    new_entry = {
        "is_cancer": is_cancer,
        "result": "Cancer Detected" if is_cancer else "No Cancer Detected",
        "confidence": confidence,
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "image": image_filename
    }

    history.insert(0, new_entry)
    history = history[:3]

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

@app.route("/save_result", methods=["POST"])
def save_result():
    data = request.json

    is_cancer = data["is_cancer"]
    confidence = data["confidence"]
    image_base64 = data["image"]  # base64 จาก frontend

    # ตั้งชื่อไฟล์
    image_filename = f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    image_path = os.path.join(UPLOAD_FOLDER, image_filename)

    # แปลง base64 -> ไฟล์รูป
    image_bytes = base64.b64decode(image_base64)
    with open(image_path, "wb") as f:
        f.write(image_bytes)

    # บันทึกลง history.json
    save_history(is_cancer, confidence, image_filename)

    return jsonify({"status": "saved", "image": image_filename})

if __name__ == "__main__":
    app.run(debug=True)
