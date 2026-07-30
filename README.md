# AgroScan – Mobile-Based Plant Disease Detection System

A final-year project that lets you point your phone camera at a plant leaf
and instantly find out if it's healthy or diseased.

---

## How It Works (Simple Explanation)

```
Phone Camera  →  JavaScript (getUserMedia)
                      ↓
              Captures frame as base64 JPEG
                      ↓
              POST /predict  (WiFi / localhost)
                      ↓
              Flask receives image
                      ↓
              PIL resizes → NumPy array → CNN model
                      ↓
              Returns: plant, disease, confidence
                      ↓
              Saved to SQLite  +  Shown on screen
```

1. **Camera** – The browser's `getUserMedia` API streams the rear camera into
   a `<video>` element. When you tap Capture, a single frame is drawn onto a
   hidden `<canvas>` and converted to a base64 JPEG string.

2. **Backend** – Flask receives the base64 string, decodes it, resizes the
   image to 128×128, and feeds it into the trained CNN. The class with the
   highest probability is returned as JSON.

3. **CNN Model** – A simple 3-block convolutional network trained on the
   PlantVillage dataset (38 disease/healthy classes). It learns visual
   patterns like leaf spots, discolouration, and texture changes.

4. **Database** – Every prediction is stored in a local SQLite file
   (`agroscan.db`) so you can review your scan history at `/history`.

---

## Project Structure

```
agroscan/
├── app.py              # Flask app (routes + prediction logic)
├── train_model.py      # CNN training script (run once)
├── database.py         # SQLite helpers
├── requirements.txt
├── model/
│   ├── agroscan_model.h5    # saved after training
│   └── class_names.json     # index → class label map
├── static/
│   ├── style.css
│   └── script.js
└── templates/
    ├── index.html      # camera / scan page
    └── history.html    # scan history page
```

---

## Setup & Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Train the model (one-time, takes ~30–60 min on CPU)

Make sure the PlantVillage dataset is at `../plantvillage dataset/color`
relative to the `agroscan/` folder, then run:

```bash
python train_model.py
```

This saves `model/agroscan_model.h5` and `model/class_names.json`.

> **Tip:** If you already have a pre-trained `.h5` file, just drop it into
> the `model/` folder along with `class_names.json` and skip this step.

### 3. Start the Flask server

```bash
python app.py
```

You should see:
```
 * Running on http://0.0.0.0:5000
```

### 4. Open on your PC

Visit: [http://localhost:5000](http://localhost:5000)

### 5. Open on your phone (same WiFi)

1. Find your PC's local IP address:
   - **Windows:** open Command Prompt → type `ipconfig` → look for
     `IPv4 Address` (e.g. `192.168.1.105`)
   - **Mac/Linux:** `ifconfig` or `ip a`

2. On your phone's browser, go to:
   ```
   http://192.168.1.105:5000
   ```
   (replace with your actual IP)

3. When the browser asks for camera permission, tap **Allow**.

4. Point the camera at a leaf → tap **Capture** → tap **Analyse**.

> **Note:** Some mobile browsers require HTTPS for camera access. If the
> camera doesn't start, try using the **"Or upload an image"** fallback
> at the bottom of the page, or run Flask behind a self-signed SSL cert.

---

## Classes Detected (38 total)

Apple, Blueberry, Cherry, Corn, Grape, Orange, Peach, Pepper, Potato,
Raspberry, Soybean, Squash, Strawberry, Tomato — both healthy and common
disease variants (scab, blight, rust, mildew, rot, etc.)

---

## Tech Stack

| Layer     | Technology                        |
|-----------|-----------------------------------|
| Frontend  | HTML5, CSS3, Vanilla JavaScript   |
| Camera    | `navigator.mediaDevices.getUserMedia` |
| Backend   | Python 3, Flask                   |
| ML Model  | TensorFlow / Keras CNN            |
| Database  | SQLite (via Python `sqlite3`)     |
| Dataset   | PlantVillage (color images)       |
