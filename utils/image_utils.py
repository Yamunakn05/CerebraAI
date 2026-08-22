# utils/image_utils.py
# ============================================================
# Image processing utilities
# ============================================================

import cv2
import numpy as np
from PIL import Image
import io
from typing import Any


def load_image_from_bytes(file_bytes: bytes) -> np.ndarray:
    """Load image from raw bytes (Streamlit uploader output)."""
    arr = np.asarray(bytearray(file_bytes), dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    return img  # BGR


def load_image_from_dicom(file_bytes: bytes) -> np.ndarray:
    """Load image from DICOM bytes using pydicom."""
    try:
        import pydicom
        ds = pydicom.dcmread(io.BytesIO(file_bytes))
        pixel_array = ds.pixel_array.astype(np.float32)
        # Normalize to 0-255
        pixel_array = (pixel_array - pixel_array.min()) / (pixel_array.max() - pixel_array.min() + 1e-8) * 255
        pixel_array = pixel_array.astype(np.uint8)
        if pixel_array.ndim == 2:
            pixel_array = cv2.cvtColor(pixel_array, cv2.COLOR_GRAY2BGR)
        return pixel_array
    except Exception as e:
        raise ValueError(f"Failed to load DICOM file: {e}")


def bgr_to_rgb(img: Any) -> np.ndarray:
    """Convert BGR (OpenCV) to RGB (Streamlit/Matplotlib)."""
    if isinstance(img, Image.Image):
        return np.array(img.convert("RGB"))
    if not isinstance(img, np.ndarray):
        img = np.array(img)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def resize_image(img: Any, size: int) -> np.ndarray:
    """Resize image to square."""
    if isinstance(img, Image.Image):
        img = np.array(img)
    elif not isinstance(img, np.ndarray):
        img = np.array(img)
    return cv2.resize(img, (size, size))


def normalize_image(img: Any) -> np.ndarray:
    """Normalize to [0, 1]."""
    if isinstance(img, Image.Image):
        img = np.array(img)
    elif not isinstance(img, np.ndarray):
        img = np.array(img)
    return img.astype("float32") / 255.0


def preprocess_for_model(img: Any, size: int = 128) -> np.ndarray:
    """Full preprocessing pipeline: resize → normalize → add batch dim."""
    if isinstance(img, Image.Image):
        img = np.array(img)
    img_resized = resize_image(img, size)
    img_norm = normalize_image(img_resized)
    return np.expand_dims(img_norm, axis=0)


def overlay_heatmap(original_img: np.ndarray, heatmap: np.ndarray, alpha: float = 0.4) -> np.ndarray:
    """Overlay a Grad-CAM heatmap on the original image."""
    heatmap_resized = cv2.resize(heatmap, (original_img.shape[1], original_img.shape[0]))
    heatmap_colored = cv2.applyColorMap(
        np.uint8(255 * heatmap_resized), cv2.COLORMAP_JET
    )
    # Convert original to BGR if RGB
    if original_img.shape[2] == 3:
        orig_bgr = original_img if original_img.dtype == np.uint8 else (original_img * 255).astype(np.uint8)
    else:
        orig_bgr = original_img
    overlay = cv2.addWeighted(orig_bgr, 1 - alpha, heatmap_colored, alpha, 0)
    return cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB)


def numpy_to_pil(img: np.ndarray) -> Image.Image:
    """Convert numpy array (RGB) to PIL Image."""
    if img.dtype != np.uint8:
        img = (img * 255).astype(np.uint8)
    return Image.fromarray(img)


def pil_to_bytes(pil_img: Image.Image, fmt: str = "PNG") -> bytes:
    """Convert PIL Image to bytes."""
    buf = io.BytesIO()
    pil_img.save(buf, format=fmt)
    return buf.getvalue()


def ensure_rgb(img: Any, is_bgr: bool = True) -> np.ndarray:
    """Ensure image is in RGB format (3 channels) as a numpy array."""
    if isinstance(img, Image.Image):
        return np.array(img.convert("RGB"))
    if not isinstance(img, np.ndarray):
        img = np.array(img)
    if img.ndim == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    if img.shape[2] == 4:
        return cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
    if img.shape[2] == 3 and is_bgr:
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img
