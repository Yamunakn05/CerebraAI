# backend/segmentation.py
# ============================================================
# Tumor Segmentation using OpenCV (Otsu + Morphology)
# ============================================================

import cv2
import numpy as np
from typing import Dict, Any, Optional


_CLAHE = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
_STRUCTURING_KERNEL = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))


def segment_tumor(img_bgr: Any, has_tumor: bool = True) -> Dict[str, Any]:
    """
    Perform tumor segmentation using adaptive thresholding + contour detection.
    Returns clean zero-mask if has_tumor is False.
    """
    if hasattr(img_bgr, "convert"):
        img_bgr = np.array(img_bgr.convert("RGB"))[:, :, ::-1] # Convert PIL to BGR
    elif not isinstance(img_bgr, np.ndarray):
        img_bgr = np.array(img_bgr)
    h, w = img_bgr.shape[:2]
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    if not has_tumor:
        mask = np.zeros((h, w), dtype=np.uint8)
        mask_rgb = np.zeros((h, w, 3), dtype=np.uint8)
        return {
            "mask": mask,
            "mask_rgb": mask_rgb,
            "overlay": img_rgb.copy(),
            "contour_img": img_rgb.copy(),
            "tumor_bbox": None,
            "tumor_area_px": 0,
            "tumor_area_pct": 0.0,
            "has_segmentation": False,
        }

    total_pixels = h * w

    # Convert to grayscale
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # Enhance contrast using a shared CLAHE instance
    enhanced = _CLAHE.apply(gray)

    # Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)

    # Otsu thresholding
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Morphological operations to clean up mask
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, _STRUCTURING_KERNEL, iterations=2)
    morph = cv2.morphologyEx(morph, cv2.MORPH_OPEN, _STRUCTURING_KERNEL, iterations=1)

    # Find contours
    contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    mask = np.zeros((h, w), dtype=np.uint8)
    tumor_bbox = None
    tumor_area_px = 0
    largest_contour = None

    if contours:
        # Filter: keep only contours in the middle 60% of the image (brain area)
        center_x, center_y = w // 2, h // 2
        margin_x, margin_y = int(w * 0.15), int(h * 0.15)
        valid = []
        for cnt in contours:
            M = cv2.moments(cnt)
            if M["m00"] == 0:
                continue
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            if margin_x < cx < w - margin_x and margin_y < cy < h - margin_y:
                valid.append(cnt)

        if not valid:
            valid = contours  # fallback: use all

        # Pick largest valid contour
        largest_contour = max(valid, key=cv2.contourArea)
        tumor_area_px = int(cv2.contourArea(largest_contour))

        # Draw filled mask
        cv2.drawContours(mask, [largest_contour], -1, 255, -1)

        # Bounding box
        x, y, bw, bh = cv2.boundingRect(largest_contour)
        tumor_bbox = (x, y, bw, bh)

    tumor_area_pct = (tumor_area_px / total_pixels) * 100

    # ── Visualization images ────────────────────────────────
    # 1. Mask overlay (red on original)
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    colored_mask = np.zeros_like(img_rgb)
    colored_mask[mask > 0] = [255, 50, 50]  # Red tumor region
    overlay = cv2.addWeighted(img_rgb, 0.7, colored_mask, 0.3, 0)

    # Draw contour + bounding box
    contour_img = img_rgb.copy()
    if largest_contour is not None:
        cv2.drawContours(contour_img, [largest_contour], -1, (0, 255, 100), 2)
        if tumor_bbox:
            x, y, bw, bh = tumor_bbox
            cv2.rectangle(contour_img, (x, y), (x + bw, y + bh), (255, 200, 0), 2)
            cv2.putText(
                contour_img,
                f"Tumor: {tumor_area_pct:.1f}%",
                (x, max(y - 8, 15)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 200, 0),
                1,
            )

    # 2. Binary mask (for display)
    mask_rgb = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)

    return {
        "mask": mask,
        "mask_rgb": mask_rgb,
        "overlay": overlay,
        "contour_img": contour_img,
        "tumor_bbox": tumor_bbox,
        "tumor_area_px": tumor_area_px,
        "tumor_area_pct": round(tumor_area_pct, 2),
        "has_segmentation": largest_contour is not None and tumor_area_px > 100,
    }


def estimate_tumor_dimensions(img_or_mask: Any, mask: Optional[np.ndarray] = None) -> Dict[str, float]:
    """Estimate tumor dimensions assuming ~1mm per pixel for standard MRI."""
    if mask is None:
        mask = img_or_mask
        h, w = mask.shape[:2]
    else:
        h, w = img_or_mask.shape[:2] if hasattr(img_or_mask, "shape") else mask.shape[:2]

    mm_per_pixel = 220.0 / max(w, 1)

    if not isinstance(mask, np.ndarray):
        mask = np.array(mask, dtype=np.uint8)

    contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return {"width_mm": 0.0, "height_mm": 0.0, "diameter_mm": 0.0}

    largest = max(contours, key=cv2.contourArea)
    x, y, bw, bh = cv2.boundingRect(largest)

    width_mm = bw * mm_per_pixel
    height_mm = bh * mm_per_pixel
    diameter_mm = ((width_mm + height_mm) / 2)

    return {
        "width_mm": round(width_mm, 1),
        "height_mm": round(height_mm, 1),
        "diameter_mm": round(diameter_mm, 1),
    }
