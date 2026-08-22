# backend/severity.py
# ============================================================
# Tumor Severity Scoring Engine
# ============================================================

from typing import Dict, Any
from utils.constants import SEVERITY_LEVELS


def calculate_severity(
    tumor_area_pct: float,
    confidence: float,
    tumor_type: str,
    brain_region: str,
) -> Dict[str, Any]:
    """
    Multi-factor severity scoring.
    Factors:
      - Tumor area (%)   → 40% weight
      - Confidence (%)   → 20% weight
      - Tumor type risk  → 25% weight
      - Brain region criticality → 15% weight

    """
    tumor_type = str(tumor_type or "").lower().strip()
    try:
        confidence = float(confidence)
    except Exception:
        confidence = 0.0
    try:
        tumor_area_pct = float(tumor_area_pct)
    except Exception:
        tumor_area_pct = 0.0

    if tumor_type == "notumor":
        return {
            "level": "None",
            "score": 0,
            "color": "#22c55e",
            "emoji": "✅",
            "explanation": (
                "No tumor was detected in this MRI scan. "
                f"The AI model classified this scan as healthy tissue with {confidence:.1f}% confidence. "
                "Continue regular health checkups as recommended by your physician."
            ),
            "factors": {
                "area_score": 0.0,
                "confidence_score": round(min(20, (confidence / 100) * 20), 1),
                "type_score": 0,
                "region_score": 0,
            },
        }

    # ── Factor 1: Tumor Area Score (0-40) ─────────────────
    area_score = min(40, (tumor_area_pct / 30) * 40)

    # ── Factor 2: Confidence Score (0-20) ─────────────────
    # High confidence + tumor detected = worse certainty of tumor presence
    conf_score = min(20, (confidence / 100) * 20)

    # ── Factor 3: Tumor Type Risk (0-25) ──────────────────
    type_risks = {
        "glioma": 25,       # Most aggressive
        "meningioma": 12,   # Usually benign
        "pituitary": 10,    # Often benign adenoma
        "notumor": 0,
    }
    type_score = type_risks.get(tumor_type, 15)

    # ── Factor 4: Brain Region Criticality (0-15) ─────────
    region_risks = {
        "Brain Stem": 15,       # Critical — vital functions
        "Frontal Lobe": 12,     # High — motor + cognition
        "Temporal Lobe": 10,
        "Parietal Lobe": 10,
        "Cerebellum": 9,
        "Occipital Lobe": 8,
        "Undetermined": 8,
    }
    region_score = region_risks.get(brain_region, 8)

    # ── Total Score ────────────────────────────────────────
    total_score = round(area_score + conf_score + type_score + region_score)
    total_score = max(0, min(100, total_score))

    # ── Classify Level ─────────────────────────────────────
    level = _score_to_level(total_score)
    level_info = SEVERITY_LEVELS[level]

    # ── Explanation ────────────────────────────────────────
    explanation = _build_explanation(level, tumor_type, tumor_area_pct, brain_region)

    return {
        "level": level,
        "score": total_score,
        "color": level_info["color"],
        "emoji": level_info["emoji"],
        "explanation": explanation,
        "factors": {
            "area_score": round(area_score, 1),
            "confidence_score": round(conf_score, 1),
            "type_score": type_score,
            "region_score": region_score,
        },
    }


def _score_to_level(score: int) -> str:
    if score < 25:
        return "Mild"
    elif score < 50:
        return "Moderate"
    elif score < 75:
        return "Severe"
    else:
        return "Critical"


def _build_explanation(level: str, tumor_type: str, area_pct: float, region: str) -> str:
    base = {
        "Mild": (
            f"The detected {tumor_type} in the {region} region appears to be at an early or "
            f"manageable stage. Tumor coverage is approximately {area_pct:.1f}% of the visible scan area. "
            f"Regular monitoring is recommended."
        ),
        "Moderate": (
            f"A moderately significant {tumor_type} has been identified in the {region} region, "
            f"covering approximately {area_pct:.1f}% of the scan area. "
            f"Medical evaluation and treatment planning are advised."
        ),
        "Severe": (
            f"A severe {tumor_type} has been detected in the {region}, with approximately "
            f"{area_pct:.1f}% scan coverage. Prompt medical intervention is strongly recommended. "
            f"This region controls critical brain functions."
        ),
        "Critical": (
            f"URGENT: A critical-severity {tumor_type} has been detected in the {region} region, "
            f"occupying approximately {area_pct:.1f}% of the scan. "
            f"Immediate neurological consultation and emergency evaluation are required."
        ),
    }
    return base.get(level, "Severity level could not be determined.")
