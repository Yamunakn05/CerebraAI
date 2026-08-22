# backend/classifier.py
# ============================================================
# Brain Tumor Classification + Grad-CAM Explainable AI
# ============================================================

import os
import sys
import threading
from typing import Dict, Any, Optional

import cv2
import numpy as np
import tensorflow as tf

from utils.constants import CLASSES, CLASS_LABELS, CLASS_INFO, IMG_SIZE, MODEL_PATH, BEST_MODEL_PATH
from utils.image_utils import preprocess_for_model, ensure_rgb

# ── Try to use Streamlit cache (graceful fallback when imported outside Streamlit) ──
# ── Model Loader (cached across reruns via module-level singleton) ──────────────
_model_cache: Optional[tf.keras.Model] = None
_model_lock = None
_grad_model_cache = None
_grad_layer_name = None


def _load_model_from_disk(path: str) -> tf.keras.Model:
    return tf.keras.models.load_model(path, compile=False)


def get_model() -> tf.keras.Model:
    """Load and cache the trained model. Thread-safe singleton."""
    global _model_cache, _model_lock
    if _model_lock is None:
        _model_lock = threading.Lock()

    if _model_cache is not None:
        return _model_cache

    with _model_lock:
        if _model_cache is not None:
            return _model_cache
        # ``brain_tumor_model.h5`` is the artifact documented in model_info.json
        # and therefore the reproducible production default.  A checkpoint is
        # only a fallback until it has been independently evaluated.
        for path in [MODEL_PATH, BEST_MODEL_PATH]:
            if os.path.exists(path):
                _model_cache = _load_model_from_disk(path)
                break
        if _model_cache is None:
            raise FileNotFoundError(
                f"No trained model found. Expected at:\n  {BEST_MODEL_PATH}\n  {MODEL_PATH}"
            )
    return _model_cache


# ── Classification ─────────────────────────────────────────
def classify_tumor(img_bgr: np.ndarray, img_rgb: Optional[np.ndarray] = None) -> Dict[str, Any]:
    """
    Run tumor classification on a BGR image (matching training channel format).
    Returns: label, confidence, all_probabilities, class_info
    """
    model = get_model()
    # The Keras model was trained on BGR images (cv2.imread default)
    x = preprocess_for_model(img_bgr, IMG_SIZE)

    predictions = model.predict(x, verbose=0)[0]
    idx = int(np.argmax(predictions))
    label = CLASSES[idx]
    confidence = float(predictions[idx]) * 100

    all_probs = {cls: float(predictions[i]) * 100 for i, cls in enumerate(CLASSES)}

    return {
        "label": label,
        "display_label": CLASS_LABELS[label],
        "confidence": confidence,
        "all_probabilities": all_probs,
        "class_info": CLASS_INFO[label],
        "has_tumor": label != "notumor",
        "prediction_idx": idx,
    }


# ── Grad-CAM ───────────────────────────────────────────────
def _get_gradcam_model() -> Optional[tf.keras.Model]:
    """Build and cache the functional Grad-CAM model once per loaded model."""
    global _grad_model_cache, _grad_layer_name
    model = get_model()
    last_conv_layer = None
    for layer in reversed(model.layers):
        if isinstance(layer, tf.keras.layers.Conv2D):
            last_conv_layer = layer
            break

    if last_conv_layer is None:
        return None

    if _grad_model_cache is not None and _grad_layer_name == last_conv_layer.name:
        return _grad_model_cache

    inputs = tf.keras.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
    traced_x = inputs
    last_conv_output = None
    for layer in model.layers:
        traced_x = layer(traced_x)
        if getattr(layer, "name", None) == last_conv_layer.name:
            last_conv_output = traced_x

    if last_conv_output is None:
        return None

    _grad_model_cache = tf.keras.Model(inputs=inputs, outputs=[last_conv_output, traced_x])
    _grad_layer_name = last_conv_layer.name
    return _grad_model_cache


def generate_gradcam(img_bgr: np.ndarray, class_idx: Optional[int] = None, img_rgb: Optional[np.ndarray] = None) -> np.ndarray:
    """
    Generate Grad-CAM heatmap for the given image.
    Returns normalized heatmap as float32 array [0, 1].
    """
    x = preprocess_for_model(img_bgr, IMG_SIZE)

    grad_model = _get_gradcam_model()
    if grad_model is None:
        return np.zeros((img_bgr.shape[0], img_bgr.shape[1]), dtype=np.float32)

    x_tensor = tf.cast(x, tf.float32)
    with tf.GradientTape(persistent=True) as tape:
        tape.watch(x_tensor)
        conv_outputs, predictions = grad_model(x_tensor)
        if class_idx is None:
            class_idx = int(tf.argmax(predictions[0]))
        class_channel = predictions[:, class_idx]

    # Gradients of class score w.r.t. conv output
    grads = tape.gradient(class_channel, conv_outputs)
    del tape  # Release persistent tape

    # Guard: if gradients are None (non-eager mode or unsupported layer), return blank
    if grads is None:
        return np.zeros((img_bgr.shape[0], img_bgr.shape[1]), dtype=np.float32)

    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    conv_outputs = conv_outputs[0]
    heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
    heatmap = tf.maximum(heatmap, 0)
    max_val = tf.math.reduce_max(heatmap)
    heatmap = heatmap / (max_val + 1e-8)

    heatmap_np = heatmap.numpy()
    # Ensure 2D output
    if heatmap_np.ndim == 0:
        return np.zeros((img_bgr.shape[0], img_bgr.shape[1]), dtype=np.float32)
    return heatmap_np.astype(np.float32)


def generate_gradcam_overlay(img_bgr: np.ndarray, class_idx: Optional[int] = None, alpha: float = 0.45, img_rgb: Optional[np.ndarray] = None) -> np.ndarray:
    """
    Generate a Grad-CAM heatmap overlaid on the original image.
    Returns RGB image as uint8.
    """
    if img_rgb is None:
        img_rgb = ensure_rgb(img_bgr)
    heatmap = generate_gradcam(img_bgr, class_idx, img_rgb=img_rgb)

    # Resize heatmap to original image size
    h, w = img_rgb.shape[:2]
    heatmap_resized = cv2.resize(heatmap, (w, h))
    heatmap_uint8 = np.uint8(255 * heatmap_resized)
    heatmap_colored = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
    heatmap_rgb = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)

    overlay = cv2.addWeighted(img_rgb, 1 - alpha, heatmap_rgb, alpha, 0)
    return overlay.astype(np.uint8)


def run_full_classification(img_bgr: np.ndarray, img_rgb: Optional[np.ndarray] = None) -> Dict[str, Any]:
    """
    Run complete classification pipeline: predict + Grad-CAM.
    Returns everything needed for the Analysis page.
    """
    if img_rgb is None:
        img_rgb = ensure_rgb(img_bgr)
    result = classify_tumor(img_bgr, img_rgb=img_rgb)
    gradcam_overlay = generate_gradcam_overlay(img_bgr, result["prediction_idx"], img_rgb=img_rgb)
    result["gradcam_overlay"] = gradcam_overlay
    return result
