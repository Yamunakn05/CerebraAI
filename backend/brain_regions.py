# backend/brain_regions.py
# ============================================================
# Brain Region Identification via Spatial Atlas Mapping
# ============================================================

import numpy as np
from typing import Dict, Any, Optional, Tuple

from utils.constants import BRAIN_REGIONS


def identify_brain_region(
    img_shape: Tuple[int, int],
    tumor_bbox: Optional[Tuple[int, int, int, int]],
    tumor_area_pct: float,
) -> Dict[str, Any]:
    """
    Map tumor location to brain region using quadrant-based spatial atlas.

    Brain region mapping (for axial MRI slices):
    ┌────────────────────────────────┐
    │     FRONTAL LOBE (top 35%)     │
    ├──────────────┬─────────────────┤
    │  PARIETAL    │   TEMPORAL      │
    │  (mid-left)  │   (mid-right)   │
    ├──────────────┴─────────────────┤
    │     OCCIPITAL (bottom 25%)     │
    └────────────────────────────────┘
    Cerebellum: bottom-center
    Brain Stem: center-bottom narrow band
    """
    h, w = img_shape[:2]

    if tumor_bbox is None or tumor_area_pct < 0.1:
        return {
            "region": "Undetermined",
            "functions": [],
            "impact": "Tumor location could not be precisely determined from this scan.",
            "confidence": "Low",
            "centroid": None,
        }

    x, y, bw, bh = tumor_bbox
    cx = x + bw // 2  # Tumor centroid X
    cy = y + bh // 2  # Tumor centroid Y

    # Normalize to [0, 1]
    nx = cx / w
    ny = cy / h

    # ── Region Mapping ─────────────────────────────────────
    region = _map_to_region(nx, ny)
    region_info = BRAIN_REGIONS.get(region, {})

    # Confidence based on tumor size (larger = more confident mapping)
    if tumor_area_pct > 5:
        confidence = "High"
    elif tumor_area_pct > 1:
        confidence = "Moderate"
    else:
        confidence = "Low"

    return {
        "region": region,
        "functions": region_info.get("functions", []),
        "impact": region_info.get("impact", ""),
        "confidence": confidence,
        "centroid": (cx, cy),
        "normalized_position": (round(nx, 3), round(ny, 3)),
    }


def _map_to_region(nx: float, ny: float) -> str:
    """Map normalized (x, y) coordinates to brain region."""
    # Frontal: top portion
    if ny < 0.35:
        return "Frontal Lobe"
    # Occipital: bottom portion
    elif ny > 0.75:
        # Differentiate cerebellum (center) from occipital (sides)
        if 0.3 < nx < 0.7:
            return "Cerebellum"
        return "Occipital Lobe"
    # Brain stem: narrow center band, lower region
    elif ny > 0.60 and 0.40 < nx < 0.60:
        return "Brain Stem"
    # Middle band
    elif ny < 0.60:
        if nx < 0.45:
            return "Parietal Lobe"
        else:
            return "Temporal Lobe"
    else:
        return "Temporal Lobe"


def get_functional_impact_summary(region: str, tumor_type: str) -> str:
    """Generate a natural-language functional impact summary."""
    if region == "Undetermined":
        return "The precise location of the tumor could not be determined from this scan."

    region_info = BRAIN_REGIONS.get(region, {})
    impact = region_info.get("impact", "")
    functions = region_info.get("functions", [])

    if not impact:
        return "No specific functional impact information available for this region."

    func_str = ", ".join(functions[:3]) if functions else "various brain functions"

    summary = (
        f"The tumor appears to be located in the **{region}**, which is primarily responsible for "
        f"{func_str}. {impact}"
    )
    if tumor_type == "glioma":
        summary += " Gliomas in this region may grow rapidly and require urgent evaluation."
    elif tumor_type == "meningioma":
        summary += " Meningiomas are typically slow-growing and may be managed conservatively."
    elif tumor_type == "pituitary":
        summary += " Pituitary tumors may additionally cause hormonal disruptions."

    return summary
