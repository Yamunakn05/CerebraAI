# evaluate_model.py
# ============================================================
# Re-evaluates the ALREADY-TRAINED model against your dataset.
# Does NOT retrain, does NOT modify brain_tumor_model.h5 or
# best_model.h5 — read-only with respect to the model weights.
#
# Run from your project root:
#     python evaluate_model.py
#
# Produces:
#   models/model_info.json         (accuracy, loss, precision, recall, f1)
#   models/confusion_matrix.png
#   models/classification_report.txt
# ============================================================

import os
import json
import random
import logging

import cv2
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, precision_score, recall_score, f1_score

# ── Config — must match main.py exactly so preprocessing is identical ──
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)

DATADIR = "dataset"
CATEGORIES = ["glioma", "meningioma", "pituitary", "notumor"]
IMG_SIZE = 128

MODEL_CANDIDATES = [
    os.path.join("models", "brain_tumor_model.h5"),
    os.path.join("models", "best_model.h5"),
]

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def find_model_path() -> str:
    for path in MODEL_CANDIDATES:
        if os.path.exists(path):
            return path
    raise FileNotFoundError(
        f"No model file found. Checked: {MODEL_CANDIDATES}"
    )


def load_dataset():
    """Identical loading logic to main.py — same order, same preprocessing,
    so the resulting train/test split (with the same SEED) reconstructs
    the same held-out test set your original training run used."""
    data = []
    for category in CATEGORIES:
        path = os.path.join(DATADIR, category)
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Dataset folder not found: {path}\n"
                f"Make sure 'dataset/glioma', 'dataset/meningioma', "
                f"'dataset/pituitary', 'dataset/notumor' exist in your "
                f"project root, same as when you trained the model."
            )
        class_num = CATEGORIES.index(category)
        images = os.listdir(path)
        logger.info(f"Loading {len(images)} images from {category}...")
        failed = 0
        for img_name in images:
            img_path = os.path.join(path, img_name)
            img_array = cv2.imread(img_path)
            if img_array is None:
                failed += 1
                continue
            img_array = cv2.resize(img_array, (IMG_SIZE, IMG_SIZE))
            data.append([img_array, class_num])
        logger.info(f"✓ {category}: {len(images) - failed}/{len(images)} loaded")

    if not data:
        raise ValueError("No images loaded — check your dataset/ folder.")

    random.shuffle(data)
    X = np.array([f for f, l in data])
    y = np.array([l for f, l in data])
    X = X.reshape(-1, IMG_SIZE, IMG_SIZE, 3).astype("float32") / 255.0
    return X, y


def main():
    model_path = find_model_path()
    logger.info(f"Loading existing model from: {model_path} (read-only, not retraining)")
    model = tf.keras.models.load_model(model_path, compile=False)

    # Recompile only to get standard metrics during .evaluate() — this does
    # NOT change the learned weights, just attaches a loss/metric config.
    model.compile(
        optimizer=tf.keras.optimizers.Adam(),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    logger.info("Loading dataset...")
    X, y = load_dataset()

    # Same split logic as main.py: 70/15/15, same SEED → same test set
    X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.15, random_state=SEED)
    logger.info(f"Reconstructed test set: {len(X_test)} images")

    logger.info("Evaluating...")
    eval_results = model.evaluate(X_test, y_test, verbose=0)
    loss = eval_results[0]
    accuracy = eval_results[1]

    y_pred = model.predict(X_test, verbose=0).argmax(axis=1)

    precision = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    recall = recall_score(y_test, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

    report = classification_report(y_test, y_pred, target_names=CATEGORIES)
    cm = confusion_matrix(y_test, y_pred)

    logger.info(f"\n=== RESULTS ===")
    logger.info(f"Test Accuracy:  {accuracy:.4f} ({100*accuracy:.2f}%)")
    logger.info(f"Test Loss:      {loss:.4f}")
    logger.info(f"Precision:      {precision:.4f}")
    logger.info(f"Recall:         {recall:.4f}")
    logger.info(f"F1 Score:       {f1:.4f}")
    logger.info(f"\n{report}")

    os.makedirs("models", exist_ok=True)

    # ── Save model_info.json ──
    model_info = {
        "accuracy": float(accuracy),
        "loss": float(loss),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        "categories": CATEGORIES,
        "img_size": IMG_SIZE,
        "test_set_size": len(X_test),
        "note": "Re-evaluated post-hoc via evaluate_model.py — original training epoch count unknown.",
        "model_file_evaluated": model_path,
    }
    with open(os.path.join("models", "model_info.json"), "w") as f:
        json.dump(model_info, f, indent=2)
    logger.info("✓ Saved models/model_info.json")

    # ── Save classification report ──
    with open(os.path.join("models", "classification_report.txt"), "w") as f:
        f.write(report)
    logger.info("✓ Saved models/classification_report.txt")

    # ── Save confusion matrix plot ──
    plt.figure(figsize=(8, 6))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues",
        xticklabels=CATEGORIES, yticklabels=CATEGORIES,
        cbar_kws={"label": "Count"},
    )
    plt.title(f"Confusion Matrix — {os.path.basename(model_path)}", fontsize=14, fontweight="bold")
    plt.ylabel("True Label")
    plt.xlabel("Predicted Label")
    plt.tight_layout()
    plt.savefig(os.path.join("models", "confusion_matrix.png"), dpi=300, bbox_inches="tight")
    plt.close()
    logger.info("✓ Saved models/confusion_matrix.png")

    logger.info("\n✅ Evaluation complete. Model weights were NOT modified.")


if __name__ == "__main__":
    main()
