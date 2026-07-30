"""
app.py  -  AgroScan Flask backend
"""

import os, json, base64, io, re
import numpy as np
from flask import (Flask, request, jsonify, render_template,
                   session, redirect, url_for)
from PIL import Image
import tensorflow as tf

from database import (init_db, register_user, login_user, get_user_by_id,
                      save_scan, get_user_scans, get_user_stats,
                      update_user, change_password)
from cures import get_cure

app = Flask(__name__)
app.secret_key = "agroscan-secret-2024"

MODEL_PATH       = os.path.join("model", "agroscan_model.h5")
CLASS_NAMES_PATH = os.path.join("model", "class_names.json")
IMG_SIZE         = (128, 128)

print("Loading model...")
model = tf.keras.models.load_model(MODEL_PATH)
with open(CLASS_NAMES_PATH) as f:
    CLASS_NAMES = {int(k): v for k, v in json.load(f).items()}

PLANT_INFO_PATH = os.path.join("model", "plant_info.json")
if os.path.exists(PLANT_INFO_PATH):
    with open(PLANT_INFO_PATH) as f:
        PLANT_INFO = {int(k): v for k, v in json.load(f).items()}
else:
    PLANT_INFO = {}

print(f"Model ready - {len(CLASS_NAMES)} classes.")
init_db()


# ── Helpers ───────────────────────────────────────────────────────────────────
def parse_label(label):
    parts   = label.split("___")
    plant   = parts[0].replace("_", " ").strip()
    disease = parts[1].replace("_", " ").strip() if len(parts) > 1 else "Unknown"
    status  = "Healthy" if "healthy" in disease.lower() else "Diseased"
    return plant, disease, status


def preprocess(image_bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize(IMG_SIZE)
    arr = np.array(img, dtype=np.float32) / 255.0
    return np.expand_dims(arr, 0)


def is_leaf_image(image_bytes: bytes) -> bool:
    """
    Heuristic leaf detector using three checks:
    1. Green dominance – leaves have more green than red/blue pixels
    2. Green pixel ratio – enough pixels must be clearly green-toned
    3. Texture variance – diagrams/screenshots are flat; leaves have texture

    Returns True if the image is likely a plant leaf.
    """
    img  = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize((128, 128))
    arr  = np.array(img, dtype=np.float32)

    R, G, B = arr[:,:,0], arr[:,:,1], arr[:,:,2]

    # ── Check 1: green channel must dominate on average ──────────────────
    mean_r, mean_g, mean_b = R.mean(), G.mean(), B.mean()
    if not (mean_g > mean_r * 0.85 and mean_g > mean_b * 0.85):
        return False

    # ── Check 2: at least 15% of pixels should be "leafy green" ─────────
    # Leafy green: G is highest channel AND G > 60 AND G - R > 5 AND G - B > 5
    green_mask = (G > R) & (G > B) & (G > 60) & ((G - R) > 5) & ((G - B) > 5)
    green_ratio = green_mask.sum() / green_mask.size
    if green_ratio < 0.15:
        return False

    # ── Check 3: texture variance – reject flat diagrams/screenshots ─────
    # Convert to grayscale and check std deviation
    gray = 0.299 * R + 0.587 * G + 0.114 * B
    if gray.std() < 15:          # very flat image = diagram/screenshot
        return False

    return True


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return decorated


# ── Auth routes ───────────────────────────────────────────────────────────────
@app.route("/login", methods=["GET"])
def login_page():
    if "user_id" in session:
        return redirect(url_for("index"))
    return render_template("login.html")


@app.route("/api/login", methods=["POST"])
def api_login():
    d = request.get_json()
    user = login_user(d.get("email", ""), d.get("password", ""))
    if user:
        session["user_id"] = user["id"]
        return jsonify({"ok": True, "name": user["full_name"]})
    return jsonify({"ok": False, "error": "Invalid email or password"}), 401


@app.route("/api/register", methods=["POST"])
def api_register():
    d = request.get_json()

    full_name = d.get("full_name", "").strip()
    email     = d.get("email", "").strip()
    phone     = d.get("phone", "").strip()
    location  = d.get("location", "").strip()
    password  = d.get("password", "")

    # Full name
    if not full_name:
        return jsonify({"ok": False, "error": "Full name is required."}), 400
    if not re.match(r"^[A-Za-z\s]+$", full_name):
        return jsonify({"ok": False, "error": "Name should contain only alphabets."}), 400
    if len(full_name) < 3 or len(full_name) > 50:
        return jsonify({"ok": False, "error": "Name must be between 3 and 50 characters."}), 400
    words = [w for w in full_name.split() if w]
    if len(words) < 2:
        return jsonify({"ok": False, "error": "Please enter your full name (first and last name)."}), 400
    if any(len(w) < 2 for w in words):
        return jsonify({"ok": False, "error": "Each part of the name must be at least 2 characters."}), 400
    if any(re.match(r"^(.)\1+$", w, re.IGNORECASE) for w in words):
        return jsonify({"ok": False, "error": "Please enter a valid real name."}), 400

    # Phone (optional)
    if phone:
        if not re.match(r"^[6-9]\d{9}$", phone):
            return jsonify({"ok": False, "error": "Please enter a valid 10-digit mobile number starting with 6-9."}), 400

    # Email
    if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
        return jsonify({"ok": False, "error": "Please enter a valid email address."}), 400

    # Location
    if not location:
        return jsonify({"ok": False, "error": "Location cannot be empty."}), 400
    if len(location) < 3:
        return jsonify({"ok": False, "error": "Location must be at least 3 characters."}), 400

    # Password
    if len(password) < 8:
        return jsonify({"ok": False, "error": "Password must be at least 8 characters."}), 400
    if not re.search(r"[A-Z]", password):
        return jsonify({"ok": False, "error": "Password must contain at least one uppercase letter."}), 400
    if not re.search(r"[a-z]", password):
        return jsonify({"ok": False, "error": "Password must contain at least one lowercase letter."}), 400
    if not re.search(r"[0-9]", password):
        return jsonify({"ok": False, "error": "Password must contain at least one number."}), 400
    if not re.search(r"[^A-Za-z0-9]", password):
        return jsonify({"ok": False, "error": "Password must contain at least one special character."}), 400

    ok, msg = register_user(full_name, email, phone, location, password)
    if ok:
        user = login_user(email, password)
        session["user_id"] = user["id"]
        return jsonify({"ok": True})
    return jsonify({"ok": False, "error": msg}), 400


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))


# ── App routes ────────────────────────────────────────────────────────────────
@app.route("/")
@login_required
def index():
    user = get_user_by_id(session["user_id"])
    return render_template("index.html", user=user)


@app.route("/history")
@login_required
def history_page():
    user = get_user_by_id(session["user_id"])
    return render_template("history.html", user=user)


@app.route("/profile")
@login_required
def profile_page():
    user  = get_user_by_id(session["user_id"])
    stats = get_user_stats(session["user_id"])
    return render_template("profile.html", user=user, stats=stats)


# ── API routes ────────────────────────────────────────────────────────────────
@app.route("/predict", methods=["POST"])
@login_required
def predict():
    data = request.get_json(silent=True)
    if not data or "image" not in data:
        return jsonify({"error": "No image provided"}), 400
    try:
        _, encoded  = data["image"].split(",", 1)
        image_bytes = base64.b64decode(encoded)
    except Exception:
        return jsonify({"error": "Invalid image format"}), 400

    try:
        # ── Leaf validation ───────────────────────────────────────────────
        if not is_leaf_image(image_bytes):
            return jsonify({
                "error": "Invalid Image! Please upload a clear plant leaf image for disease detection."
            }), 422

        preds      = model.predict(preprocess(image_bytes))[0]
        idx        = int(np.argmax(preds))
        confidence = float(preds[idx]) * 100

        # ── Low-confidence guard (model unsure = not a known leaf class) ─
        if confidence < 40:
            return jsonify({
                "error": "Invalid Image! Please upload a clear plant leaf image for disease detection."
            }), 422

        if idx in PLANT_INFO:
            plant   = PLANT_INFO[idx]["plant"]
            disease = PLANT_INFO[idx]["disease"]
            status  = PLANT_INFO[idx]["status"]
        else:
            plant, disease, status = parse_label(CLASS_NAMES[idx])

        save_scan(session["user_id"], plant, disease, status, confidence)
        cure = get_cure(disease)
        return jsonify({
            "plant":      plant,
            "disease":    disease,
            "status":     status,
            "confidence": round(confidence, 2),
            "cure":       cure,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/cure/<path:disease>")
@login_required
def api_cure(disease):
    return jsonify(get_cure(disease))


@app.route("/api/profile/update", methods=["POST"])
@login_required
def api_profile_update():
    d         = request.get_json()
    full_name = d.get("full_name", "").strip()
    phone     = d.get("phone", "").strip()
    location  = d.get("location", "").strip()
    if not full_name:
        return jsonify({"ok": False, "error": "Name cannot be empty"}), 400
    update_user(session["user_id"], full_name, phone, location)
    return jsonify({"ok": True, "full_name": full_name})


@app.route("/api/profile/password", methods=["POST"])
@login_required
def api_change_password():
    d = request.get_json()
    ok, msg = change_password(
        session["user_id"],
        d.get("old_password", ""),
        d.get("new_password", ""),
    )
    if ok:
        return jsonify({"ok": True, "message": msg})
    return jsonify({"ok": False, "error": msg}), 400


@app.route("/api/history")
@login_required
def api_history():
    return jsonify(get_user_scans(session["user_id"]))


@app.route("/api/stats")
@login_required
def api_stats():
    return jsonify(get_user_stats(session["user_id"]))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
