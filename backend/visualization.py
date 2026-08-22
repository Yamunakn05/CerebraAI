# backend/visualization.py
# ============================================================
# Brain Tumor Imaging & Grad-CAM Visualizations
# ============================================================

import io
import cv2
import numpy as np
from typing import Optional, Tuple, Dict, Any
from PIL import Image


def create_gradcam_overlay(
    original_img: np.ndarray,
    heatmap: np.ndarray,
    alpha: float = 0.4,
    colormap: int = cv2.COLORMAP_JET,
) -> np.ndarray:
    """
    Overlay Grad-CAM heatmap on the original MRI image.
    """
    if original_img is None or heatmap is None:
        return original_img

    if original_img.dtype != np.uint8:
        original_img = np.clip(original_img, 0, 255).astype(np.uint8)

    if original_img.ndim == 2:
        original_img = cv2.cvtColor(original_img, cv2.COLOR_GRAY2RGB)

    heatmap_resized = cv2.resize(heatmap, (original_img.shape[1], original_img.shape[0]))
    if heatmap_resized.dtype != np.uint8:
        heatmap_resized = (heatmap_resized * 255).astype(np.uint8)

    color_heatmap = cv2.applyColorMap(heatmap_resized, colormap)
    color_heatmap = cv2.cvtColor(color_heatmap, cv2.COLOR_BGR2RGB)

    overlay = cv2.addWeighted(original_img, 1 - alpha, color_heatmap, alpha, 0)
    return overlay


def draw_tumor_contour(
    original_img: np.ndarray,
    mask: np.ndarray,
    color: Tuple[int, int, int] = (255, 0, 0),
    thickness: int = 2,
) -> np.ndarray:
    """
    Draw segmented tumor contour on the original MRI image.
    """
    if original_img is None or mask is None:
        return original_img

    if original_img.dtype != np.uint8:
        original_img = np.clip(original_img, 0, 255).astype(np.uint8)

    if original_img.ndim == 2:
        img_out = cv2.cvtColor(original_img, cv2.COLOR_GRAY2RGB)
    else:
        img_out = original_img.copy()

    contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(img_out, contours, -1, color, thickness)
    return img_out


def encode_image_to_png_bytes(img: np.ndarray) -> bytes:
    """Convert numpy array image to PNG bytes."""
    if img is None:
        return b""
    if img.dtype != np.uint8:
        img = np.clip(img, 0, 255).astype(np.uint8)
    if img.ndim == 2:
        pil = Image.fromarray(img, mode="L")
    else:
        pil = Image.fromarray(img, mode="RGB")

    buf = io.BytesIO()
    pil.save(buf, format="PNG")
    return buf.getvalue()
