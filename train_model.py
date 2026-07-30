

import os, json
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# ── Config ────────────────────────────────────────────────────────────────────
DATASET_DIR = "../plantvillage dataset/color"
MODEL_DIR   = "model"
MODEL_PATH  = os.path.join(MODEL_DIR, "agroscan_model.h5")
IMG_SIZE    = (128, 128)
BATCH_SIZE  = 32
EPOCHS      = 10

os.makedirs(MODEL_DIR, exist_ok=True)

# ── Data ──────────────────────────────────────────────────────────────────────
datagen = ImageDataGenerator(
    rescale=1.0 / 255,
    validation_split=0.2,
    rotation_range=20,
    horizontal_flip=True,
    zoom_range=0.2,
)

train_gen = datagen.flow_from_directory(
    DATASET_DIR, target_size=IMG_SIZE, batch_size=BATCH_SIZE,
    class_mode="categorical", subset="training", shuffle=True,
)
val_gen = datagen.flow_from_directory(
    DATASET_DIR, target_size=IMG_SIZE, batch_size=BATCH_SIZE,
    class_mode="categorical", subset="validation", shuffle=False,
)

NUM_CLASSES = len(train_gen.class_indices)
print(f"Classes: {NUM_CLASSES}  |  Train: {train_gen.samples}  |  Val: {val_gen.samples}")

# ── Save class_names.json & plant_info.json ───────────────────────────────────
idx_to_class = {v: k for k, v in train_gen.class_indices.items()}

with open(os.path.join(MODEL_DIR, "class_names.json"), "w") as f:
    json.dump(idx_to_class, f, indent=2)

def parse_label(label):
    parts   = label.split("___")
    plant   = parts[0].replace("_", " ").strip()
    disease = parts[1].replace("_", " ").strip() if len(parts) > 1 else "Unknown"
    status  = "Healthy" if "healthy" in disease.lower() else "Diseased"
    return plant, disease, status

plant_info = {}
for idx, label in idx_to_class.items():
    p, d, s = parse_label(label)
    plant_info[idx] = {"plant": p, "disease": d, "status": s}

with open(os.path.join(MODEL_DIR, "plant_info.json"), "w") as f:
    json.dump(plant_info, f, indent=2)

print("JSON files saved.")

# ── Model ─────────────────────────────────────────────────────────────────────
model = models.Sequential([
    layers.Input(shape=(*IMG_SIZE, 3)),

    layers.Conv2D(32, (3,3), activation="relu", padding="same"),
    layers.MaxPooling2D(),

    layers.Conv2D(64, (3,3), activation="relu", padding="same"),
    layers.MaxPooling2D(),

    layers.Conv2D(128, (3,3), activation="relu", padding="same"),
    layers.MaxPooling2D(),

    layers.Flatten(),
    layers.Dense(256, activation="relu"),
    layers.Dropout(0.4),
    layers.Dense(NUM_CLASSES, activation="softmax"),
])

model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
model.summary()

# ── Train ─────────────────────────────────────────────────────────────────────
model.fit(
    train_gen,
    validation_data=val_gen,
    epochs=EPOCHS,
    callbacks=[
        tf.keras.callbacks.ModelCheckpoint(
            MODEL_PATH, save_best_only=True, monitor="val_accuracy", verbose=1
        ),
        tf.keras.callbacks.EarlyStopping(
            patience=3, restore_best_weights=True, monitor="val_accuracy"
        ),
    ],
)

print(f"\n✅ Model saved to {MODEL_PATH}")
print("Now run:  python app.py")
