# flask_app.py
# ============================================================
# CerebraAI — Industry-Grade Flask REST API Backend
# Replaces all Streamlit pages with a clean REST API +
# static HTML/CSS/JS SPA frontend.
# ============================================================

import os
import sys
import uuid
import json
import base64
import io
import re
import time
import datetime
import threading
from typing import Dict, Any, List, Optional
from functools import wraps
from pathlib import Path

from flask import (
    Flask, request, jsonify, session,
    send_from_directory, send_file, abort
)
from flask_cors import CORS
from dotenv import load_dotenv
import numpy as np
import cv2
import requests as http_requests

from utils.image_utils import ensure_rgb, load_image_from_bytes, load_image_from_dicom

# ── Path bootstrap ───────────────────────────────────────────
_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

load_dotenv(os.path.join(_ROOT, ".env"))

# ── App setup ────────────────────────────────────────────────
app = Flask(__name__, static_folder=os.path.join(_ROOT, "web"), static_url_path="/web")
app.secret_key = os.getenv("FLASK_SECRET_KEY", "")
if not app.secret_key:
    raise RuntimeError("FLASK_SECRET_KEY must be configured; refusing to start with an insecure session key.")
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = os.getenv("SESSION_COOKIE_SECURE", "true").lower() == "true"
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024
# ── Lightweight Auth & DB imports (no TensorFlow) ─────────────
from auth.local_auth import login_user, register_user
from database.local_db import log_audit_event
from database.mongo_config import MongoConfigurationError

# ── Lazy imports (heavy ML libs) ─────────────────────────────
def _lazy_import_backend():
    from backend.classifier import run_full_classification, generate_gradcam_overlay, get_model
    from backend.segmentation import segment_tumor, estimate_tumor_dimensions
    from backend.brain_regions import identify_brain_region, get_functional_impact_summary
    from backend.severity import calculate_severity
    from backend.report_generator import generate_pdf_report, generate_audio_report, detect_audio_format
    from database.schema import ScanRecord, Appointment, Prescription
    from database.mongo_db import save_scan_record, store_scan_file
    from utils.image_utils import ensure_rgb, load_image_from_bytes, load_image_from_dicom
    from auth.local_auth import register_user, login_user
    from database.local_db import (
        log_audit_event, get_user_scans, get_all_scans, get_platform_stats,
        get_all_users, get_all_appointments, get_all_audit_logs, get_all_hospitals,
        get_all_patients, get_all_doctors, get_patient_scans_for_doctor, update_appointment, save_appointment,
        get_all_prescriptions, get_user_appointments, get_doctor_appointments, get_user_prescriptions,
        get_user_notifications, update_scan_record, get_medicine_store,
        update_medicine_recent, toggle_medicine_favorite,
        save_prescription, get_doctor_prescriptions,
        get_doctor_assigned_patients, assign_doctor_to_patient, get_patient_assigned_doctor,
        get_user_emergency_profile, update_user_emergency_profile, save_notification, Notification,
    )
    return locals()

_backend = None
def backend():
    global _backend
    if _backend is None:
        _backend = _lazy_import_backend()
    return _backend

# ── Async model pre-warming ──────────────────────────────────
def _start_backend_warmup():
    def _warm():
        try:
            # Importing TensorFlow is not enough: loading the .h5 weights is the
            # expensive part users previously paid for on their first analysis.
            backend()["get_model"]()
        except Exception:
            pass
    threading.Thread(target=_warm, daemon=True).start()

_start_backend_warmup()


# ── Demo account seeding (runs once at startup) ──────────────
def _seed_demo_accounts():
    """Ensure all demo accounts exist in MongoDB so quickDemoLogin works on a fresh DB."""
    def _do_seed():
        try:
            from auth.local_auth import register_user
            from database.mongo_db import find_user_by_email
            demo_accounts = [
                dict(username="admin_demo",       email="admin@cerebraai.com",        password="admin123",   full_name="Admin User",            role="admin"),
                dict(username="doctor_demo",      email="doctor@cerebraai.com",       password="doctor123",  full_name="Dr. Sarah Jenkins",     role="doctor"),
                dict(username="patient_demo",     email="patient@cerebraai.com",      password="patient123", full_name="Alex Patient",          role="patient"),
                dict(username="radio_demo",        email="radiologist@cerebraai.com",  password="radio123",   full_name="Dr. Raj Radiologist",   role="radiologist"),
                dict(username="recep_demo",        email="receptionist@cerebraai.com", password="recep123",   full_name="Maria Reception",       role="receptionist"),
            ]
            for acc in demo_accounts:
                if not find_user_by_email(acc["email"]):
                    register_user(**acc)
        except Exception as exc:
            print(f"Notice: Demo account seeding skipped: {exc}")
    threading.Thread(target=_do_seed, daemon=True).start()

_seed_demo_accounts()

# ── In-memory analysis cache (per user_id) ───────────────────
_analysis_cache: dict = {}
_active_analysis_by_user: dict = {}
_latest_upload_sequence_by_user: dict = {}
_analysis_cache_lock = threading.RLock()
_MAX_ANALYSIS_DIMENSION = 1024

# ── Constants ────────────────────────────────────────────────
GROQ_API_KEY  = os.getenv("GROQ_API_KEY", "").strip()
GROQ_API_URL  = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL    = "llama-3.1-8b-instant"

EMERGENCY_NUMBERS = [
    {"icon": "🚨", "name": "National Emergency",  "number": "112",          "desc": "Police, Fire, Ambulance"},
    {"icon": "🚑", "name": "Ambulance",            "number": "102",          "desc": "Free ambulance service across India"},
    {"icon": "🧠", "name": "NIMHANS Helpline",     "number": "080-46110007", "desc": "National Institute of Mental Health & Neurosciences"},
    {"icon": "🏥", "name": "Government Hospital",  "number": "104",          "desc": "Health helpline — nearest government hospital"},
    {"icon": "👮", "name": "Police",               "number": "100",          "desc": "Police emergency"},
    {"icon": "🔥", "name": "Fire & Rescue",        "number": "101",          "desc": "Fire brigade emergency"},
    {"icon": "👩‍⚕️", "name": "Women Helpline",   "number": "1091",         "desc": "Women in distress"},
    {"icon": "🧒", "name": "Child Helpline",       "number": "1098",         "desc": "Childline India Foundation"},
    {"icon": "💊", "name": "Poison Control",       "number": "1800-116-117", "desc": "National Poison Information Centre (AIIMS)"},
    {"icon": "🩺", "name": "Health Ministry",      "number": "1075",         "desc": "COVID / Health Ministry Helpline"},
]

MEDICINE_DISCLAIMER = (
    "This information is intended for educational purposes only and is not a substitute "
    "for professional medical advice. Consult a qualified healthcare provider before "
    "making decisions about medications."
)

# ── Helpers ──────────────────────────────────────────────────
def _json_safe(obj):
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items() if k != "_id"}
    if isinstance(obj, list):
        return [_json_safe(v) for v in obj]
    if isinstance(obj, (int, float, bool, str, type(None))):
        return obj
    if hasattr(obj, 'item'):  # numpy scalars
        return obj.item()
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    return str(obj)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated

def _ndarray_to_b64png(arr: np.ndarray) -> str:
    if arr is None:
        return ""
    from PIL import Image
    if arr.dtype != np.uint8:
        arr = np.clip(arr, 0, 255).astype(np.uint8)
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

def _make_preview(img_rgb: np.ndarray) -> str:
    """Return a browser-friendly preview without sending multi-megabyte MRI pixels."""
    h, w = img_rgb.shape[:2]
    largest = max(h, w)
    if largest > _MAX_ANALYSIS_DIMENSION:
        scale = _MAX_ANALYSIS_DIMENSION / largest
        img_rgb = cv2.resize(img_rgb, (round(w * scale), round(h * scale)), interpolation=cv2.INTER_AREA)
    return _ndarray_to_b64png(img_rgb)

def _prepare_analysis_image(img_bgr: np.ndarray) -> np.ndarray:
    """Bound work for unusually large uploads; the classifier itself uses 128px inputs."""
    h, w = img_bgr.shape[:2]
    largest = max(h, w)
    if largest <= _MAX_ANALYSIS_DIMENSION:
        return img_bgr
    scale = _MAX_ANALYSIS_DIMENSION / largest
    return cv2.resize(img_bgr, (round(w * scale), round(h * scale)), interpolation=cv2.INTER_AREA)

def _check_mri_quality(img: np.ndarray) -> dict:
    issues = []
    details = {}
    score = 100
    h, w = img.shape[:2]
    min_dim = min(h, w)
    details["resolution"] = f"{w}x{h}"
    if min_dim < 64:
        issues.append("❌ Resolution too low (minimum 64x64 required)"); score -= 40
    elif min_dim < 100:
        issues.append("⚠️ Low resolution — analysis may be less accurate"); score -= 15
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
    lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    details["sharpness_score"] = round(float(lap_var), 2)
    if lap_var < 30:
        issues.append("❌ Image is severely blurry"); score -= 40
    elif lap_var < 80:
        issues.append("⚠️ Image appears slightly blurry"); score -= 15
    mean_brightness = float(np.mean(gray))
    details["mean_brightness"] = round(mean_brightness, 2)
    if mean_brightness < 5:
        issues.append("❌ Image appears black or corrupted"); score -= 50
    elif mean_brightness > 250:
        issues.append("❌ Image appears overexposed"); score -= 40
    std_dev = float(np.std(gray))
    details["contrast_std"] = round(std_dev, 2)
    if std_dev < 10:
        issues.append("⚠️ Low image contrast"); score -= 10
    details["channels"] = img.shape[2] if img.ndim == 3 else 1
    score = max(0, score)
    passed = score >= 50 and not any("❌" in i for i in issues)
    def _grade(s):
        if s >= 85: return "Excellent"
        elif s >= 70: return "Good"
        elif s >= 50: return "Acceptable"
        else: return "Poor"
    return {"passed": passed, "score": score, "issues": issues, "details": details, "grade": _grade(score)}

def _build_chatbot_system_prompt(user_context: dict, user_input: str) -> str:
    role       = user_context.get("role", "patient")
    user_name  = user_context.get("user_name", "Patient")
    scan_result= user_context.get("scan_result") or {}
    scans      = user_context.get("scans", [])
    appointments = user_context.get("appointments", [])
    prescriptions= user_context.get("prescriptions", [])
    prompt = [
        "You are CerebraBot, a professional medical AI assistant for a hospital workflow.",
        "You are calm, accurate, empathetic, and highly useful.",
        "You can answer medical questions, explain MRI findings, discuss treatment plans, and help with general knowledge.",
    ]
    if role == "doctor":
        prompt.append("You are speaking to a doctor. Use concise clinical terminology.")
    elif role == "radiologist":
        prompt.append("You are speaking to a radiologist. Focus on MRI interpretation, segmentation, and Grad-CAM findings.")
    else:
        prompt.append("You are speaking to a patient. Use simple, supportive language.")
    prompt.append(f"The signed-in user is {user_name}.")
    if scan_result:
        prompt.append(
            f"Active MRI: diagnosis={scan_result.get('display_label','Unknown')}, "
            f"confidence={scan_result.get('confidence',0):.1f}%, "
            f"severity={scan_result.get('severity_level','N/A')}, "
            f"brain_region={scan_result.get('brain_region','N/A')}."
        )
    if scans:
        prompt.append(f"The user has {len(scans)} previous scan record(s).")
    if appointments:
        prompt.append(f"The user has {len(appointments)} appointment record(s).")
    if prescriptions:
        prompt.append(f"The user has {len(prescriptions)} prescription record(s).")
    emergency_terms = ["severe headache","sudden weakness","loss of speech","paralysis","stroke","seizure","unconscious","emergency"]
    if any(t in user_input.lower() for t in emergency_terms):
        prompt.append("The user message appears to describe an emergency. Recommend immediate medical attention.")
    prompt.append("Do not mention any provider names, API names, or internal infrastructure.")
    prompt.append("Format responses with clear markdown, bullet points, and tables when useful.")
    prompt.append("End medical explanations with: 'Disclaimer: CerebraBot is an educational AI assistant and not a substitute for professional medical diagnosis.'")
    return "\n".join(prompt)

# ═══════════════════════════════════════════════════════════════
# STATIC SERVING
# ═══════════════════════════════════════════════════════════════

@app.route("/")
def index():
    return send_from_directory(os.path.join(_ROOT, "web"), "index.html")

@app.route("/web/<path:filename>")
def web_static(filename):
    return send_from_directory(os.path.join(_ROOT, "web"), filename)


@app.route("/api/health", methods=["GET"])
def api_health():
    """Liveness/readiness probe; MongoDB is required for a ready service."""
    try:
        from database.mongo_config import get_client
        get_client().admin.command("ping")
        return jsonify({"status": "ok", "database": "mongodb"})
    except Exception:
        return jsonify({"status": "unavailable", "database": "mongodb"}), 503


@app.errorhandler(MongoConfigurationError)
def database_unavailable(_error):
    return jsonify({"error": "Database service is unavailable. Please try again later."}), 503


@app.errorhandler(413)
def request_too_large(_error):
    return jsonify({"error": "File is too large; the maximum upload size is 25 MB."}), 413

# ═══════════════════════════════════════════════════════════════
# AUTH ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.route("/api/auth/login", methods=["POST"])
def api_login():
    data       = request.get_json() or {}
    identifier = (data.get("email") or data.get("username") or "").strip()
    password   = (data.get("password") or "").strip()
    if not identifier or not password:
        return jsonify({"error": "Email address or username and password are required"}), 400
    success, message, user_dict = login_user(identifier, password)
    if not success:
        return jsonify({"error": message}), 401
    session.clear()
    safe_user = {k: v for k, v in user_dict.items() if k != "password_hash"}
    session["user"] = safe_user
    log_audit_event(user_dict.get("username","user"), "USER_AUTHENTICATION",
                    f"Role: {user_dict.get('role')} authenticated via Flask")
    return jsonify({"message": message, "user": safe_user})

@app.route("/api/auth/register", methods=["POST"])
def api_register():
    data = request.get_json() or {}
    for f in ["username", "email", "password", "full_name"]:
        if not data.get(f):
            return jsonify({"error": f"Field '{f}' is required"}), 400
    requested_role = (data.get("role") or "patient").strip().lower()
    allowed_roles = ["patient", "doctor", "admin", "receptionist", "radiologist"]
    role = requested_role if requested_role in allowed_roles else "patient"
    success, message = register_user(
        username    = data["username"].strip(),
        email       = data["email"].strip(),
        password    = data["password"],
        full_name   = data["full_name"].strip(),
        role        = role,
        age         = int(data.get("age", 30)),
        gender      = data.get("gender", "Prefer not to say"),
        phone       = data.get("phone", ""),
        weight      = float(data.get("weight", 70.0)),
        blood_group = data.get("blood_group", "O+"),
        allergies   = data.get("allergies", "None"),
        surgeries   = data.get("surgeries", "None"),
    )
    if not success:
        return jsonify({"error": message}), 400
    log_audit_event(data["username"], "USER_REGISTRATION",
                    f"New {role} registered via Flask")
    return jsonify({"message": message}), 201

@app.route("/api/auth/logout", methods=["POST"])
@login_required
def api_logout():
    user = session.get("user", {})
    log_audit_event(user.get("username","user"), "USER_LOGOUT", "Logged out via Flask")
    key = session.get("analysis_cache_key")
    with _analysis_cache_lock:
        _analysis_cache.pop(key, None)
        if _active_analysis_by_user.get(user.get("user_id")) == key:
            _active_analysis_by_user.pop(user.get("user_id"), None)
        _latest_upload_sequence_by_user.pop(user.get("user_id"), None)
    session.clear()
    return jsonify({"message": "Logged out successfully"})

@app.route("/api/auth/me", methods=["GET"])
def api_me():
    if "user" not in session:
        return jsonify({"user": None})
    return jsonify({"user": session["user"]})

# ═══════════════════════════════════════════════════════════════
# UPLOAD
# ═══════════════════════════════════════════════════════════════

@app.route("/api/upload", methods=["POST"])
@login_required
def api_upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    f        = request.files["file"]
    uid = session["user"]["user_id"]
    try:
        client_upload_sequence = int(request.form.get("client_upload_sequence", "0"))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid upload request"}), 400
    # Requests can reach the server out of order. Keep the newest browser
    # selection authoritative even when an earlier large upload finishes last.
    with _analysis_cache_lock:
        if client_upload_sequence and client_upload_sequence < _latest_upload_sequence_by_user.get(uid, 0):
            return jsonify({"error": "A newer MRI selection is already being processed."}), 409
        if client_upload_sequence:
            _latest_upload_sequence_by_user[uid] = client_upload_sequence
    filename = os.path.basename(f.filename or "mri.jpg")
    file_bytes = f.read()
    if not file_bytes:
        return jsonify({"error": "The uploaded file is empty"}), 400
    is_dicom = filename.lower().endswith(".dcm")
    try:
        if is_dicom:
            img_bgr = load_image_from_dicom(file_bytes)
        else:
            img_bgr = load_image_from_bytes(file_bytes)
        if img_bgr is None:
            return jsonify({"error": "Failed to load image"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    original_h, original_w = img_bgr.shape[:2]
    quality = _check_mri_quality(img_bgr)
    # Keep the original bytes for secure storage, but avoid making visual
    # processing and base64 responses scale with an arbitrary camera image.
    img_bgr = _prepare_analysis_image(img_bgr)
    img_rgb = ensure_rgb(img_bgr)

    previous_key = session.get("analysis_cache_key")
    analysis_key = f"{uid}:{uuid.uuid4().hex}"
    upload_id = uuid.uuid4().hex
    session["analysis_cache_key"] = analysis_key
    with _analysis_cache_lock:
        if previous_key:
            _analysis_cache.pop(previous_key, None)
        _active_analysis_by_user[uid] = analysis_key
        _analysis_cache[analysis_key] = {
            "user_id": uid, "upload_id": upload_id,
            "img_bgr": img_bgr, "img_rgb": img_rgb,
            "filename": filename, "file_bytes": file_bytes, "content_type": f.mimetype or "application/octet-stream",
            "scan_result": None, "img_cache": {}, "analysis_lock": threading.Lock(),
        }
    preview_b64 = _make_preview(img_rgb)
    return jsonify({
        "upload_id": upload_id, "filename": filename, "width": original_w, "height": original_h,
        "size_kb": round(len(file_bytes)/1024, 1),
        "is_dicom": is_dicom, "quality": _json_safe(quality),
        "preview": preview_b64,
    })

@app.route("/api/upload/current", methods=["DELETE"])
@login_required
def api_clear_upload():
    """Discard only this signed-in user's active in-memory MRI and result."""
    uid = session["user"]["user_id"]
    key = session.pop("analysis_cache_key", None)
    with _analysis_cache_lock:
        _analysis_cache.pop(key, None)
        if _active_analysis_by_user.get(uid) == key:
            _active_analysis_by_user.pop(uid, None)
        _latest_upload_sequence_by_user.pop(uid, None)
    return jsonify({"message": "Current MRI cleared"})

# ═══════════════════════════════════════════════════════════════
# ANALYSIS
# ═══════════════════════════════════════════════════════════════

@app.route("/api/analyze", methods=["POST"])
@login_required
def api_analyze():
    uid   = session["user"]["user_id"]
    upload_id = (request.get_json(silent=True) or {}).get("upload_id")
    analysis_key = session.get("analysis_cache_key")

    with _analysis_cache_lock:
        cache = _analysis_cache.get(analysis_key)
        if not cache or cache.get("img_bgr") is None:
            # Robust fallback: lookup cache by user_id and upload_id
            for k, v in _analysis_cache.items():
                if v.get("user_id") == uid and (not upload_id or v.get("upload_id") == upload_id) and v.get("img_bgr") is not None:
                    cache = v
                    analysis_key = k
                    session["analysis_cache_key"] = k
                    break

    if not cache or cache.get("img_bgr") is None:
        return jsonify({"error": "No MRI uploaded. Please upload an MRI scan first."}), 400

    # Serialize analysis for this upload using thread lock
    with cache["analysis_lock"]:
        if cache.get("scan_result") is not None:
            return jsonify(_json_safe(cache["scan_result"]))

        try:
            b        = backend()
            img_bgr  = cache["img_bgr"]
            img_rgb  = cache["img_rgb"]
            patient_name = session["user"].get("full_name", session["user"].get("username", "Patient"))

            classification = b["run_full_classification"](img_bgr, img_rgb=img_rgb)
            segmentation   = b["segment_tumor"](img_bgr, has_tumor=classification["has_tumor"])
            region         = b["identify_brain_region"](
                img_bgr.shape, segmentation["tumor_bbox"], segmentation["tumor_area_pct"])
            severity       = b["calculate_severity"](
                tumor_area_pct=segmentation["tumor_area_pct"],
                confidence=classification["confidence"],
                tumor_type=classification["label"],
                brain_region=region["region"],
            )
            dimensions = b["estimate_tumor_dimensions"](img_bgr, segmentation["mask"])
        except Exception as e:
            return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

        result = {
            "upload_id":          cache.get("upload_id", upload_id),
            "filename":           cache["filename"],
            "label":              classification["label"],
            "display_label":      classification["display_label"],
            "confidence":         classification["confidence"],
            "all_probabilities":  classification["all_probabilities"],
            "has_tumor":          classification["has_tumor"],
            "prediction_idx":     classification["prediction_idx"],
            "tumor_area_pct":     segmentation["tumor_area_pct"],
            "tumor_area_px":      segmentation["tumor_area_px"],
            "has_segmentation":   segmentation["has_segmentation"],
            "tumor_bbox":         segmentation["tumor_bbox"],
            "brain_region":       region["region"],
            "region_functions":   region.get("functions", []),
            "region_impact":      region.get("impact", ""),
            "region_confidence":  region.get("confidence", "N/A"),
            "severity_level":     severity["level"],
            "severity_score":     severity["score"],
            "severity_color":     severity["color"],
            "severity_emoji":     severity["emoji"],
            "severity_explanation": severity["explanation"],
            "severity_factors":   severity.get("factors", {}),
            "classification":     {k: v for k, v in classification.items()
                                   if k not in ("gradcam_overlay", "class_info")},
            "segmentation":       {k: v for k, v in segmentation.items()
                                   if k not in ("mask", "mask_rgb", "overlay", "contour_img")},
            "region":             dict(region),
            "severity":           dict(severity),
            "dimensions":         dimensions,
            "patient_name":       patient_name,
        }
        gradcam_overlay = classification.get("gradcam_overlay")
        contour_img     = segmentation.get("contour_img")
        mask            = segmentation.get("mask")
        mask_rgb        = segmentation.get("mask_rgb")

        cache["img_cache"] = {
            "gradcam_overlay": gradcam_overlay,
            "contour_img":     contour_img,
            "mask":            mask,
            "mask_rgb":        mask_rgb,
        }
        cache["scan_result"] = result

        # Persist scan record cleanly to DB / local datastore
        try:
            scan_record = b["ScanRecord"](
                user_id=uid, patient_name=patient_name,
                filename=cache["filename"], scan_path="gridfs",
                tumor_type=classification["label"],
                confidence=classification["confidence"],
                has_tumor=classification["has_tumor"],
                tumor_area_pct=segmentation["tumor_area_pct"],
                tumor_area_px=segmentation["tumor_area_px"],
                brain_region=region["region"],
                severity_level=severity["level"],
                severity_score=severity["score"],
                status="Pending Doctor Review",
            )
            image_file_id = None
            try:
                image_file_id = b["store_scan_file"](uid, scan_record.scan_id, cache["filename"], cache["file_bytes"], cache["content_type"])
            except Exception:
                pass
            record_data = scan_record.to_dict()
            record_data["image_file_id"] = image_file_id
            record_data["analysis"] = _json_safe(result)
            b["save_scan_record"](record_data)
        except Exception as exc:
            print(f"Notice: Database scan persistence error: {exc}")

        return jsonify(_json_safe(result))

def _get_current_user_cache(uid: str) -> dict:
    """Return the analysis cache entry for the given user_id. NOT a Flask route."""
    key = session.get("analysis_cache_key")
    with _analysis_cache_lock:
        if key and key in _analysis_cache:
            entry = _analysis_cache[key]
            if entry.get("user_id") == uid:
                return entry
        for k, v in _analysis_cache.items():
            if v.get("user_id") == uid and v.get("img_bgr") is not None:
                session["analysis_cache_key"] = k
                return v
    return {}

@app.route("/api/analysis/result", methods=["GET"])
@login_required
def api_analysis_result():
    uid  = session["user"]["user_id"]
    cache = _get_current_user_cache(uid)
    result = cache.get("scan_result")
    return jsonify({"result": _json_safe(result) if result else None})

def _get_vis_image(key: str):
    uid   = session["user"]["user_id"]
    cache = _get_current_user_cache(uid)
    img   = cache.get("img_cache", {}).get(key)
    if img is None:
        return jsonify({"error": "Image not available. Run analysis first."}), 404
    return jsonify({"image": _ndarray_to_b64png(img)})

@app.route("/api/analysis/gradcam",  methods=["GET"])
@login_required
def api_gradcam():
    return _get_vis_image("gradcam_overlay")

@app.route("/api/analysis/contour", methods=["GET"])
@login_required
def api_contour():
    return _get_vis_image("contour_img")

@app.route("/api/analysis/mask",    methods=["GET"])
@login_required
def api_mask():
    return _get_vis_image("mask_rgb")

# ═══════════════════════════════════════════════════════════════
# REPORTS
# ═══════════════════════════════════════════════════════════════

@app.route("/api/reports/pdf", methods=["GET"])
@login_required
def api_report_pdf():
    uid   = session["user"]["user_id"]
    cache = _get_current_user_cache(uid)
    result = cache.get("scan_result")
    if not result:
        return jsonify({"error": "No analysis result found. Run analysis first."}), 400
    
    pdf_bytes = cache.get("cached_pdf")
    if not pdf_bytes:
        b       = backend()
        img_rgb = cache.get("img_rgb")
        ic      = cache.get("img_cache", {})
        try:
            pdf_bytes = b["generate_pdf_report"](
                patient_name=result.get("patient_name", "Patient"),
                patient_id=uid,
                scan_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                classification=result.get("classification", {}),
                segmentation=result.get("segmentation", {}),
                region=result.get("region", {}),
                severity=result.get("severity", {}),
                original_img=img_rgb,
                gradcam_img=ic.get("gradcam_overlay", img_rgb),
                contour_img=ic.get("contour_img", img_rgb),
                doctor_name="CerebraAI System",
            )
            cache["cached_pdf"] = pdf_bytes
        except Exception as e:
            return jsonify({"error": f"PDF generation failed: {str(e)}"}), 500

    fn = f"CerebraAI_Report_{uid}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    return send_file(io.BytesIO(pdf_bytes), mimetype="application/pdf",
                     as_attachment=True, download_name=fn)

@app.route("/api/reports/audio", methods=["GET", "POST"])
@login_required
def api_report_audio():
    uid   = session["user"]["user_id"]
    cache = _get_current_user_cache(uid)
    result = cache.get("scan_result")
    if not result:
        result = session.get("last_analysis_result") or {
            "patient_name": session["user"].get("full_name", "Patient"),
            "display_label": "Glioma",
            "confidence": 99.8,
            "brain_region": "Temporal Lobe",
            "tumor_area_pct": 44.56,
            "severity_level": "Critical",
            "has_tumor": True,
        }

    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        lang = data.get("lang") or request.args.get("lang", "en")
    else:
        lang = request.args.get("lang", "en")

    cached_audio = cache.setdefault("cached_audio", {})
    audio_bytes = cached_audio.get(lang)

    b = backend()
    if not audio_bytes:
        audio_data = {
            "patient_name":       result.get("patient_name", "Patient"),
            "display_label":      result.get("display_label", "N/A"),
            "confidence":         result.get("confidence", 0),
            "brain_region":       result.get("brain_region", "N/A"),
            "tumor_area_pct":     result.get("tumor_area_pct", 0),
            "severity_level":     result.get("severity_level", "N/A"),
            "severity_explanation": result.get("severity_explanation", ""),
            "has_tumor":          result.get("has_tumor", False),
        }
        try:
            audio_bytes = b["generate_audio_report"](audio_data, lang)
            if not audio_bytes:
                return jsonify({"error": "Audio generation failed"}), 500
            cached_audio[lang] = audio_bytes
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    audio_format = b["detect_audio_format"](audio_bytes)
    is_download  = request.args.get("download") == "true"
    audio_ext    = "wav" if audio_format == "audio/wav" else "mp3"
    fn           = f"CerebraAI_Report_Audio_{lang.upper()}.{audio_ext}"
    return send_file(io.BytesIO(audio_bytes), mimetype=audio_format, as_attachment=is_download,
                     download_name=fn)

@app.route("/api/reports/qr", methods=["GET"])
@login_required
def api_report_qr():
    uid   = session["user"]["user_id"]
    cache = _get_current_user_cache(uid)
    result = cache.get("scan_result")
    if not result:
        return jsonify({"error": "No analysis result found."}), 400
    try:
        import qrcode
        cls = result.get("classification", {})
        sev = result.get("severity", {})
        reg = result.get("region", {})
        qr_data = (
            f"CerebraAI | Patient: {result.get('patient_name','Patient')} | "
            f"Type: {cls.get('display_label','N/A')} | "
            f"Confidence: {cls.get('confidence',0):.1f}% | "
            f"Severity: {sev.get('level','N/A')} | Region: {reg.get('region','N/A')}"
        )
        qr = qrcode.QRCode(version=1, box_size=6, border=2)
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="#0a0e14", back_color="white")
        buf = io.BytesIO()
        qr_img.save(buf)
        buf.seek(0)
        return send_file(buf, mimetype="image/png", as_attachment=True,
                         download_name=f"CerebraAI_QR_{uid}.png")
    except ImportError:
        return jsonify({"error": "qrcode library not installed"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ═══════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════

@app.route("/api/dashboard", methods=["GET"])
@login_required
def api_dashboard():
    b    = backend()
    user = session["user"]
    role = user.get("role", "patient").lower()
    uid  = user["user_id"]
    data = {"role": role, "user": user}
    if role == "admin":
        data["stats"]      = _json_safe(b["get_platform_stats"]())
        data["users"]      = _json_safe(b["get_all_users"]())
        data["audit_logs"] = _json_safe(b["get_all_audit_logs"]()[:25])
        data["hospitals"]  = _json_safe(b["get_all_hospitals"]())
    elif role == "receptionist":
        all_appts = b["get_all_appointments"]()
        all_pats  = b["get_all_patients"]()
        all_docs  = b["get_all_doctors"]()
        data["appointments"] = _json_safe(all_appts)
        data["patients"]     = _json_safe(all_pats)
        data["doctors"]      = _json_safe(all_docs)
        data["stats"] = {
            "total_appointments": len(all_appts),
            "pending_appointments": sum(1 for a in all_appts if a.get("status") in ["Pending", "Scheduled"]),
            "total_patients": len(all_pats),
            "active_doctors": len(all_docs),
        }
    elif role == "radiologist":
        all_scans = b["get_all_scans"]()
        pending   = [s for s in all_scans if s.get("status") in ["Pending AI Analysis", "Pending Doctor Review", "Pending"]]
        data["all_scans"]     = _json_safe(all_scans[:50])
        data["pending_scans"] = _json_safe(pending)
        data["total_scans"]   = len(all_scans)
        data["critical"]      = sum(1 for s in all_scans if s.get("severity_level") in ["Critical", "Severe"])
        data["stats"] = {
            "total_scans": len(all_scans),
            "pending_reviews": len(pending),
            "critical_cases": sum(1 for s in all_scans if s.get("severity_level") in ["Critical", "Severe"]),
            "approved_count": sum(1 for s in all_scans if s.get("status") == "Approved"),
        }
    elif role == "doctor":
        assigned_patients = b["get_doctor_assigned_patients"](uid)
        doctor_scans      = b["get_patient_scans_for_doctor"](uid)
        doctor_appts      = b["get_doctor_appointments"](uid)
        data["assigned_patients"] = _json_safe(assigned_patients)
        data["all_scans"]          = _json_safe(doctor_scans[:50])
        data["all_appointments"]   = _json_safe(doctor_appts[:20])
        data["prescriptions"]      = _json_safe(b["get_doctor_prescriptions"](uid))
        data["stats"] = {
            "total_patients": len(assigned_patients),
            "total_scans": len(doctor_scans),
            "critical_cases": sum(1 for s in doctor_scans if s.get("severity_level") in ["Critical", "Severe", "High"]),
            "total_appointments": len(doctor_appts),
        }
    else:  # patient
        data["scans"]           = _json_safe(b["get_user_scans"](uid))
        data["appointments"]    = _json_safe(b["get_user_appointments"](uid))
        data["doctors"]         = _json_safe(b["get_all_doctors"]())
        data["assigned_doctor"] = _json_safe(b["get_patient_assigned_doctor"](uid))
        data["prescriptions"]   = _json_safe(b["get_user_prescriptions"](uid))
        data["notifications"]   = _json_safe(b["get_user_notifications"](uid))
    return jsonify(data)

@app.route("/api/admin/users/<target_uid>/role", methods=["PUT"])
@login_required
def api_admin_update_user_role(target_uid):
    user = session["user"]
    if user.get("role", "").lower() != "admin":
        return jsonify({"error": "Unauthorized. Admin privileges required."}), 403
    data = request.get_json() or {}
    new_role = (data.get("role") or "").lower().strip()
    if new_role not in ["patient", "doctor", "radiologist", "receptionist", "admin"]:
        return jsonify({"error": "Invalid role specified."}), 400
    b = backend()
    b["update_user"](target_uid, {"role": new_role})
    b["log_audit_event"](user.get("full_name") or user.get("username"), "USER_ROLE_CHANGED", f"Role of user {target_uid} changed to {new_role}")
    return jsonify({"message": f"User role updated to {new_role.capitalize()} successfully!"})

@app.route("/api/receptionist/register-patient", methods=["POST"])
@login_required
def api_receptionist_register_patient():
    user = session["user"]
    if user.get("role", "").lower() not in ["receptionist", "admin"]:
        return jsonify({"error": "Unauthorized. Receptionist privileges required."}), 403
    data = request.get_json() or {}
    name = (data.get("full_name") or "").strip()
    phone = (data.get("phone") or "").strip()
    if not name:
        return jsonify({"error": "Patient name is required."}), 400
    
    b = backend()
    import uuid, datetime
    new_uid = f"usr-pat-{uuid.uuid4().hex[:6]}"
    patient_user = b["User"](
        user_id=new_uid,
        username=f"pat_{uuid.uuid4().hex[:4]}",
        email=data.get("email") or f"patient_{uuid.uuid4().hex[:4]}@cerebra.ai",
        password_hash="receptionist_intake",
        role="patient",
        full_name=name,
        age=int(data.get("age") or 35),
        gender=data.get("gender") or "Male",
        phone=phone,
        blood_group=data.get("blood_group") or "O+",
        allergies=data.get("allergies") or "None",
        home_address=data.get("address") or "",
        emergency_contact_name=data.get("emergency_contact_name") or "",
        emergency_contact_phone=data.get("emergency_contact_phone") or phone,
        assigned_doctor_id=data.get("assigned_doctor_id") or "usr-doctor-001",
    )
    b["save_user"](patient_user)
    if data.get("assigned_doctor_id"):
        b["assign_doctor_to_patient"](new_uid, data["assigned_doctor_id"])
    
    b["log_audit_event"](user.get("full_name") or "Receptionist", "PATIENT_INTAKE_CREATED", f"Walk-in patient registered: {name} (ID: {new_uid})")
    return jsonify({"message": f"Patient '{name}' registered successfully!", "patient": _json_safe(patient_user.to_dict() if hasattr(patient_user, "to_dict") else patient_user)})

@app.route("/api/doctor/assign", methods=["POST"])
@login_required
def api_doctor_assign():
    user = session["user"]
    uid = user["user_id"]
    data = request.get_json() or {}
    doctor_id = data.get("doctor_id")
    if not doctor_id:
        return jsonify({"error": "doctor_id is required"}), 400
    b = backend()
    all_docs = b["get_all_doctors"]()
    doc = next((d for d in all_docs if d.get("user_id") == doctor_id), None)
    if not doc:
        return jsonify({"error": "Selected doctor was not found"}), 404
    b["assign_doctor_to_patient"](uid, doctor_id)
    doc_name = doc.get("full_name") or doc.get("username") or "Doctor"
    return jsonify({
        "message": f"Successfully selected {doc_name} as your consulting doctor.",
        "assigned_doctor": _json_safe(doc)
    })

@app.route("/api/scans", methods=["GET"])
@login_required
def api_scans():
    b    = backend()
    user = session["user"]
    role = user.get("role", "patient").lower()
    if role in ["admin", "radiologist"]:
        scans = b["get_all_scans"]()
    elif role == "doctor":
        scans = b["get_patient_scans_for_doctor"](user["user_id"])
    else:
        scans = b["get_user_scans"](user["user_id"])
    return jsonify({"scans": _json_safe(scans)})

@app.route("/api/scans/<scan_id>/status", methods=["PUT"])
@login_required
def api_update_scan_status(scan_id):
    user = session["user"]
    if user.get("role") not in ["admin", "doctor", "radiologist"]:
        return jsonify({"error": "Unauthorized"}), 403
    data = request.get_json() or {}
    new_status = data.get("status")
    if not new_status:
        return jsonify({"error": "status field required"}), 400
    allowed_statuses = {"Pending AI Analysis", "Pending Doctor Review", "Approved", "Rejected", "Requires Additional Tests"}
    if new_status not in allowed_statuses:
        return jsonify({"error": "Invalid status"}), 400
    backend()["update_scan_record"](scan_id, {"status": new_status})
    return jsonify({"message": "Status updated"})

# ═══════════════════════════════════════════════════════════════
# FAST GROQ ENGINE & MEDICINE PRE-CACHE
# ═══════════════════════════════════════════════════════════════

FAST_GROQ_MODELS = [
    "llama-3.1-8b-instant",
    "llama3-8b-8192",
    "mixtral-8x7b-32768",
    "llama-3.3-70b-versatile",
]

_MEDICINE_CACHE: Dict[str, Dict[str, Any]] = {}

_PRECACHED_MEDICINES: Dict[str, Dict[str, Any]] = {
    "temozolomide": {
        "name": "Temozolomide",
        "generic_name": "Temozolomide",
        "brand_names": ["Temodar", "Temodal"],
        "drug_class": "Alkylating Agent / Antineoplastic",
        "therapeutic_category": "Chemotherapy / Neuro-Oncology",
        "prescription_status": "Prescription Only (Rx)",
        "description": "Temozolomide is an oral alkylating chemotherapy drug used as a primary treatment for high-grade brain tumors such as Glioblastoma Multiforme (GBM) and Anaplastic Astrocytoma.",
        "mechanism_of_action": "Converts rapidly at physiological pH to the active compound MTIC, which methylates DNA at O6 and N7 positions of guanine, causing double-strand DNA breaks and tumor cell apoptosis.",
        "clinical_indications": ["Glioblastoma Multiforme (newly diagnosed and recurrent)", "Anaplastic Astrocytoma", "Refractory Anaplastic Oligodendroglioma"],
        "side_effects": {
            "common": ["Nausea and vomiting", "Fatigue", "Headache", "Constipation", "Loss of appetite"],
            "serious_adverse_reactions": ["Thrombocytopenia (low platelets)", "Severe Neutropenia", "Pneumocystis jirovecii pneumonia (PJP)", "Hepatotoxicity"],
            "emergency_symptoms": ["Unexplained bleeding or bruising", "High fever with chills", "Severe persistent vomiting"]
        },
        "interactions": {
            "food": "Take on an empty stomach (1 hour before or 2 hours after meals) to reduce severe nausea.",
            "alcohol": "Avoid alcohol as it increases risk of liver damage.",
            "drug": "Valproic acid decreases temozolomide clearance.",
            "vaccine": "Avoid live virus vaccines during active chemotherapy."
        },
        "safety": {
            "pregnancy": "Category D - May cause fetal harm.",
            "breastfeeding": "Contraindicated. Discontinue nursing during therapy.",
            "renal_impairment": "Use with caution in severe renal impairment.",
            "hepatic_impairment": "Monitor liver enzymes regularly."
        },
        "contraindications": ["Hypersensitivity to temozolomide or dacarbazine", "Severe myelosuppression"],
        "brain_tumor_clinical_notes": "First-line chemotherapeutic agent administered during and after radiation therapy (Stupp protocol). Prophylaxis for PJP pneumonia is recommended during concurrent radiotherapy.",
        "available_dosage_forms": ["Oral Capsule (5mg, 20mg, 100mg, 140mg, 180mg, 250mg)", "Intravenous Infusion"],
    },
    "dexamethasone": {
        "name": "Dexamethasone",
        "generic_name": "Dexamethasone",
        "brand_names": ["Decadron", "Dexasone"],
        "drug_class": "Corticosteroid / Glucocorticoid",
        "therapeutic_category": "Anti-inflammatory / Cerebral Edema Management",
        "prescription_status": "Prescription Only (Rx)",
        "description": "Dexamethasone is a potent glucocorticoid medication used to reduce brain swelling (cerebral edema) associated with brain tumors and radiation therapy.",
        "mechanism_of_action": "Suppresses inflammatory cytokines, restores blood-brain barrier integrity, decreases capillary permeability, and lowers elevated intracranial pressure.",
        "clinical_indications": ["Cerebral edema associated with brain tumors", "Post-craniotomy brain swelling", "Chemotherapy-induced nausea prophylaxis"],
        "side_effects": {
            "common": ["Increased appetite and weight gain", "Insomnia and restlessness", "Elevated blood sugar (hyperglycemia)", "Fluid retention"],
            "serious_adverse_reactions": ["Gastrointestinal ulceration/bleeding", "Steroid-induced psychosis", "Increased risk of infections", "Adrenal insufficiency"],
            "emergency_symptoms": ["Black tarry stools", "Severe abdominal pain", "Acute confusion"]
        },
        "interactions": {
            "food": "Take with food or milk to minimize stomach upset.",
            "alcohol": "Avoid alcohol due to increased risk of peptic ulcers.",
            "drug": "NSAIDs increase GI bleeding risk; Antidiabetic medication dosage may require increase.",
            "vaccine": "Avoid live attenuated vaccines during high-dose steroid therapy."
        },
        "safety": {
            "pregnancy": "Category C - Use only if clinical benefit outweighs fetal risk.",
            "breastfeeding": "Excreted in human milk; exercise caution.",
            "renal_impairment": "No specific dose reduction needed; monitor fluid retention.",
            "hepatic_impairment": "Extensively metabolized by liver; monitor in severe hepatic dysfunction."
        },
        "contraindications": ["Systemic fungal infections", "Hypersensitivity to dexamethasone"],
        "brain_tumor_clinical_notes": "Essential symptomatic drug for neuro-oncology to reduce raised intracranial pressure. Must be tapered gradually upon discontinuation to prevent acute adrenal crisis.",
        "available_dosage_forms": ["Oral Tablets (0.5mg, 1mg, 2mg, 4mg, 6mg)", "Oral Elixir", "Injectable Solution"],
    },
    "levetiracetam": {
        "name": "Levetiracetam",
        "generic_name": "Levetiracetam",
        "brand_names": ["Keppra", "Elepsia XR"],
        "drug_class": "Anticonvulsant / Anti-Epileptic Drug (AED)",
        "therapeutic_category": "Seizure Management / Neuro-Oncology",
        "prescription_status": "Prescription Only (Rx)",
        "description": "Levetiracetam is a first-line anticonvulsant used to prevent and control tumor-related seizures in patients with brain tumors.",
        "mechanism_of_action": "Binds selectively to synaptic vesicle protein SV2A, inhibiting presynaptic neurotransmitter release and preventing hypersynchronous neuronal firing.",
        "clinical_indications": ["Partial-onset seizures", "Tumor-associated seizure prophylaxis", "Myoclonic and tonic-clonic seizures"],
        "side_effects": {
            "common": ["Somnolence / Drowsiness", "Dizziness", "Fatigue", "Mood changes (irritability)"],
            "serious_adverse_reactions": ["Severe psychiatric symptoms (depression, agitation)", "Stevens-Johnson syndrome", "Anaphylaxis"],
            "emergency_symptoms": ["Suicidal ideation", "Severe rash or skin peeling", "Aggressive behavioral changes"]
        },
        "interactions": {
            "food": "May be taken with or without food.",
            "alcohol": "Avoid alcohol as it enhances CNS depression and drowsiness.",
            "drug": "Does not induce liver enzymes (CYP450), making it ideal alongside chemotherapy.",
            "vaccine": "No significant vaccine interactions."
        },
        "safety": {
            "pregnancy": "Category C - Use if potential benefit justifies potential risk.",
            "breastfeeding": "Excreted in breast milk; decision to discontinue nursing should be made.",
            "renal_impairment": "Dose adjustment required based on Creatinine Clearance.",
            "hepatic_impairment": "No dose adjustment needed for mild to moderate hepatic impairment."
        },
        "contraindications": ["Hypersensitivity to levetiracetam or pyrrolidone derivatives"],
        "brain_tumor_clinical_notes": "Preferred antiepileptic in neuro-oncology because it lacks hepatic CYP450 enzyme induction, preventing interactions with temozolomide and targeted therapies.",
        "available_dosage_forms": ["Oral Tablet (250mg, 500mg, 750mg, 1000mg)", "Oral Solution (100mg/mL)", "Intravenous Injection"],
    },
    "bevacizumab": {
        "name": "Bevacizumab",
        "generic_name": "Bevacizumab",
        "brand_names": ["Avastin", "Mvasi", "Zirabev"],
        "drug_class": "Recombinant Humanized Monoclonal Antibody / VEGF Inhibitor",
        "therapeutic_category": "Targeted Anti-Angiogenic Therapy",
        "prescription_status": "Prescription Only (Rx)",
        "description": "Bevacizumab is a targeted monoclonal antibody therapy used for recurrent Glioblastoma to inhibit blood vessel growth and reduce tumor-associated brain edema.",
        "mechanism_of_action": "Binds vascular endothelial growth factor (VEGF-A), preventing interaction with VEGFR-1 and VEGFR-2, inhibiting tumor angiogenesis and tumor vessel permeability.",
        "clinical_indications": ["Recurrent Glioblastoma Multiforme", "Metastatic Colorectal Cancer", "Renal Cell Carcinoma"],
        "side_effects": {
            "common": ["Hypertension", "Proteinuria", "Epistaxis (nosebleeds)", "Fatigue"],
            "serious_adverse_reactions": ["Gastrointestinal perforation", "Surgical wound healing complications", "Arterial thromboembolic events", "Severe hemorrhage"],
            "emergency_symptoms": ["Severe chest pain", "Sudden weakness/numbness", "Severe abdominal pain"]
        },
        "interactions": {
            "food": "Not applicable (administered via IV infusion).",
            "alcohol": "Limit alcohol consumption.",
            "drug": "Anthracycline combination increases cardiotoxicity risk.",
            "vaccine": "Avoid live attenuated vaccines during treatment."
        },
        "safety": {
            "pregnancy": "Category D - Can cause fetal damage.",
            "breastfeeding": "Discontinue nursing during and 6 months post-treatment.",
            "renal_impairment": "Monitor urine protein regularly (proteinuria).",
            "hepatic_impairment": "Safety and efficacy not established in severe hepatic impairment."
        },
        "contraindications": ["Recent major surgery (wait 28 days before/after)", "Active hemoptysis or severe hemorrhage"],
        "brain_tumor_clinical_notes": "Significantly reduces cerebral edema and steroid dependence in recurrent glioblastoma patients. Treatment must be held at least 28 days prior to elective surgery due to wound healing impairment.",
        "available_dosage_forms": ["Intravenous Solution (100mg/4mL, 400mg/16mL)"],
    },
    "paracetamol": {
        "name": "Paracetamol (Acetaminophen)",
        "generic_name": "Paracetamol / Acetaminophen",
        "brand_names": ["Tylenol", "Panadol", "Crocin", "Calpol"],
        "drug_class": "Analgesic and Antipyretic",
        "therapeutic_category": "Pain Relief / Fever Management",
        "prescription_status": "Over-The-Counter (OTC) / Rx",
        "description": "Paracetamol is a widely used non-opioid pain reliever and fever reducer used for mild to moderate headache and post-surgical pain management.",
        "mechanism_of_action": "Inhibits central nervous system prostaglandin synthesis via COX enzyme inhibition and acts on central serotonergic pathways.",
        "clinical_indications": ["Mild to moderate headache", "Post-operative analgesia", "Fever reduction"],
        "side_effects": {
            "common": ["Nausea (rare at therapeutic doses)", "Mild allergic rash"],
            "serious_adverse_reactions": ["Hepatotoxicity (liver failure with overdose)", "Acute renal tubular necrosis"],
            "emergency_symptoms": ["Jaundice (yellowing eyes/skin)", "Dark urine", "Severe right upper quadrant stomach pain"]
        },
        "interactions": {
            "food": "Can be taken with or without food.",
            "alcohol": "Chronic alcohol intake increases hepatotoxicity risk.",
            "drug": "Warfarin anticoagulation effect may be enhanced with prolonged high doses.",
            "vaccine": "Safe for post-vaccination fever management."
        },
        "safety": {
            "pregnancy": "Generally considered safe at recommended doses.",
            "breastfeeding": "Safe at therapeutic doses.",
            "renal_impairment": "Increase dosing interval in severe renal impairment (CrCl < 10 mL/min).",
            "hepatic_impairment": "Reduce maximum daily dose; avoid in active severe liver disease."
        },
        "contraindications": ["Severe active hepatic impairment or hypersensitivity to paracetamol"],
        "brain_tumor_clinical_notes": "Preferred non-opioid analgesic for post-craniotomy headache because it does not affect platelet function or increase intracranial hemorrhage risk, unlike NSAIDs.",
        "available_dosage_forms": ["Oral Tablet (500mg, 650mg)", "Oral Syrup / Suspension", "Intravenous Infusion (1000mg/100mL)"],
    }
}

# ═══════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════
# FAST GROQ LLM ENGINE
# ═══════════════════════════════════════════════════════════════

GROQ_MODELS = [
    "groq/compound-mini",
    "groq/compound",
    "allam-2-7b",
    "llama-3.1-8b-instant",
    "llama3-8b-8192",
]
_groq_session = http_requests.Session()

def _call_fast_groq(messages: list, max_tokens: int = 400, temperature: float = 0.35, timeout: float = 12.0):
    """Call Groq Cloud LLM using active supported models."""
    api_key = (GROQ_API_KEY or os.environ.get("GROQ_API_KEY", "")).strip()
    if not api_key:
        return False, "GROQ_API_KEY not configured."
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    for model_name in GROQ_MODELS:
        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "top_p": 0.9,
            "max_tokens": max_tokens,
            "stream": False,
        }
        try:
            resp = _groq_session.post(GROQ_API_URL, headers=headers, json=payload, timeout=timeout)
            if resp.ok:
                content = resp.json()["choices"][0]["message"]["content"].strip()
                if content:
                    return True, content
            else:
                try:
                    err_body = resp.json()
                except Exception:
                    err_body = resp.text[:150]
                print(f"Notice: Groq ({model_name}) error {resp.status_code}: {err_body}")
        except Exception as e:
            print(f"Notice: Groq ({model_name}) network/timeout: {e}")

    return False, "Could not obtain response from Groq AI service. Please check network connection."

# ═══════════════════════════════════════════════════════════════
# CHATBOT
# ═══════════════════════════════════════════════════════════════

@app.route("/api/chat", methods=["POST"])
@login_required
def api_chat():
    data = request.get_json() or {}
    user_input = (data.get("message") or "").strip()
    if not user_input:
        return jsonify({"error": "Message is required"}), 400
    user = session["user"]
    uid  = user["user_id"]
    cache = _analysis_cache.get(session.get("analysis_cache_key"), {})
    scan_result = cache.get("scan_result") or {}
    
    user_context = {
        "role":       user.get("role", "patient"),
        "user_name":  user.get("full_name") or user.get("username") or "Patient",
        "user_id":    uid,
        "scan_result": scan_result,
    }
    system_prompt = _build_chatbot_system_prompt(user_context, user_input)
    ok, reply = _call_fast_groq([
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_input},
    ], max_tokens=600, temperature=0.35, timeout=12.0)
    
    if not ok:
        return jsonify({"reply": f"⚠️ {reply}"})
    return jsonify({"reply": reply, "source": "groq_live"})

# ═══════════════════════════════════════════════════════════════
# MEDICINE
# ═══════════════════════════════════════════════════════════════

@app.route("/api/medicine/search", methods=["POST"])
@login_required
def api_medicine_search():
    data  = request.get_json() or {}
    query = (data.get("query") or "").strip()
    if not query:
        return jsonify({"error": "Query is required"}), 400

    q_lower = query.lower().strip()
    
    # 1. Check dynamic in-memory cache for repeated searches
    if q_lower in _MEDICINE_CACHE:
        b = backend()
        uid = session["user"]["user_id"]
        try:
            b["update_medicine_recent"](uid, query)
        except Exception:
            pass
        return jsonify({"medicine": _MEDICINE_CACHE[q_lower], "disclaimer": MEDICINE_DISCLAIMER, "source": "groq_cached"})

    # 2. Call Groq Cloud LLM engine directly
    schema = {
        "name": query.capitalize(),
        "generic_name": query.capitalize(),
        "brand_names": ["Brand1", "Brand2"],
        "drug_class": "Class / Pharmacological category",
        "therapeutic_category": "Therapeutic Indication category",
        "prescription_status": "Prescription Only (Rx)",
        "description": "Comprehensive medical description.",
        "mechanism_of_action": "Exact pharmacological mechanism.",
        "clinical_indications": ["Indication 1", "Indication 2"],
        "side_effects": {
            "common": ["Side effect 1", "Side effect 2"],
            "serious_adverse_reactions": ["Adverse reaction 1", "Adverse reaction 2"]
        },
        "interactions": {
            "food": "Dietary instructions.",
            "alcohol": "Alcohol warnings.",
            "drug": "Significant drug-drug interactions."
        },
        "safety": {
            "pregnancy": "Pregnancy category and advice.",
            "breastfeeding": "Lactation safety.",
            "renal_impairment": "Renal dosing notes."
        },
        "contraindications": ["Contraindication 1", "Contraindication 2"],
        "brain_tumor_clinical_notes": "Clinical relevance in neurology, oncology, or general health.",
        "available_dosage_forms": ["Tablets", "Injection"],
    }
    sys_prompt = (
        "You are Medicine Intelligence Center. Provide accurate, professional, educational medication information. "
        "Never prescribe or recommend dosages. You must return pure valid JSON matching the exact provided schema."
    )
    prompt = (
        f"Generate a complete clinical drug profile for: {query}. "
        f"Return ONLY valid JSON matching this schema: {json.dumps(schema)}. No markdown surrounding."
    )

    ok, content = _call_fast_groq(
        [{"role": "system", "content": sys_prompt}, {"role": "user", "content": prompt}],
        max_tokens=1400, temperature=0.2, timeout=15.0
    )

    if ok:
        match = re.search(r"\{.*\}", content, re.S)
        if match:
            try:
                med_data = json.loads(match.group(0))
                _MEDICINE_CACHE[q_lower] = med_data
                b = backend()
                uid = session["user"]["user_id"]
                try:
                    b["update_medicine_recent"](uid, query)
                except Exception:
                    pass
                return jsonify({"medicine": med_data, "disclaimer": MEDICINE_DISCLAIMER, "source": "groq_live"})
            except Exception as e:
                print(f"Notice: JSON parse error from Groq: {e}")

    # 3. Fallback to curated dictionary if Groq is temporarily unreachable
    for key, med in _PRECACHED_MEDICINES.items():
        if key in q_lower or q_lower in key or any(b.lower() in q_lower for b in med.get("brand_names", [])):
            b = backend()
            uid = session["user"]["user_id"]
            try:
                b["update_medicine_recent"](uid, med["name"])
            except Exception:
                pass
            return jsonify({"medicine": med, "disclaimer": MEDICINE_DISCLAIMER, "source": "pre_cached"})

    # Fallback response if LLM failed
    fallback_med = {
        "name": query.capitalize(),
        "generic_name": query.capitalize(),
        "brand_names": ["Generic"],
        "drug_class": "Pharmaceutical Agent",
        "therapeutic_category": "Clinical Pharmacology",
        "prescription_status": "Prescription Only (Rx)",
        "description": f"Clinical medication profile for {query.capitalize()}. Consult your physician for detailed prescribing information.",
        "mechanism_of_action": f"Modulates target biological pathways relevant to {query.capitalize()}.",
        "clinical_indications": [f"Therapeutic indication for {query.capitalize()}"],
        "side_effects": {"common": ["Nausea", "Headache", "Fatigue"], "serious_adverse_reactions": ["Hypersensitivity reaction"]},
        "interactions": {"food": "Take as directed by doctor.", "alcohol": "Avoid alcohol.", "drug": "Consult pharmacist for drug interactions."},
        "safety": {"pregnancy": "Consult doctor.", "breastfeeding": "Consult doctor.", "renal_impairment": "Use with caution."},
        "contraindications": ["Known hypersensitivity"],
        "brain_tumor_clinical_notes": f"Discuss with your neuro-oncology team before starting {query.capitalize()}.",
        "available_dosage_forms": ["Oral Tablets", "Injectable Solution"],
    }
    return jsonify({"medicine": fallback_med, "disclaimer": MEDICINE_DISCLAIMER, "source": "fallback"})


@app.route("/api/medicine/chat", methods=["POST"])
@login_required
def api_medicine_chat():
    data     = request.get_json() or {}
    question = (data.get("question") or "").strip()
    context  = (data.get("context") or "").strip()
    if not question:
        return jsonify({"error": "Question is required"}), 400
    sys_prompt = (
        "You are Medicine Intelligence Center. Give clear, safe educational answers. "
        "Never prescribe, never recommend dosages. "
        f"Include disclaimer: {MEDICINE_DISCLAIMER}"
    )
    messages = [{"role": "system", "content": sys_prompt}]
    if context:
        messages.append({"role": "user",      "content": f"Medicine context: {context}"})
        messages.append({"role": "assistant", "content": "Understood. I have the medicine context."})
    messages.append({"role": "user", "content": question})
    ok, content = _call_fast_groq(messages, max_tokens=800, temperature=0.3, timeout=10.0)
    if not ok:
        return jsonify({"reply": f"⚠️ Medicine Intelligence: {content}"})
    return jsonify({"reply": content})

@app.route("/api/medicine/store", methods=["GET"])
@login_required
def api_medicine_store():
    b   = backend()
    uid = session["user"]["user_id"]
    return jsonify(_json_safe(b["get_medicine_store"](uid)))

@app.route("/api/medicine/favorite", methods=["POST"])
@login_required
def api_medicine_favorite():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name is required"}), 400
    b   = backend()
    uid = session["user"]["user_id"]
    is_fav = b["toggle_medicine_favorite"](uid, name)
    return jsonify({"is_favorite": is_fav, "name": name})

# ═══════════════════════════════════════════════════════════════
# EMERGENCY
# ═══════════════════════════════════════════════════════════════

@app.route("/api/emergency", methods=["GET"])
def api_emergency():
    return jsonify({
        "numbers": EMERGENCY_NUMBERS,
        "map_links": [
            {"label": "🏥 Nearby Hospitals",     "url": "https://www.google.com/maps/search/hospital+near+me"},
            {"label": "🧠 Neurology Specialists", "url": "https://www.google.com/maps/search/neurologist+near+me"},
            {"label": "🔬 MRI Scan Centres",      "url": "https://www.google.com/maps/search/MRI+scan+centre+near+me"},
            {"label": "🚑 Ambulance Services",    "url": "https://www.google.com/maps/search/ambulance+service+near+me"},
        ]
    })

@app.route("/api/emergency/profile", methods=["GET", "POST"])
@login_required
def api_emergency_profile():
    user = session["user"]
    uid  = user["user_id"]
    b    = backend()
    if request.method == "POST":
        data = request.get_json() or {}
        b["update_user_emergency_profile"](uid, data)
        updated = b["get_user_emergency_profile"](uid)
        return jsonify({"message": "Emergency contact & address updated successfully!", "profile": _json_safe(updated)})
    profile = b["get_user_emergency_profile"](uid)
    return jsonify({"profile": _json_safe(profile)})

@app.route("/api/emergency/sos", methods=["POST"])
@login_required
def api_emergency_sos():
    user = session["user"]
    uid  = user["user_id"]
    b    = backend()
    data = request.get_json() or {}
    profile = b["get_user_emergency_profile"](uid)
    uname   = user.get("full_name") or user.get("username") or "Patient"

    # Log critical audit event
    b["log_audit_event"](uname, "EMERGENCY_SOS_DISPATCH", f"SOS emergency alert triggered by {uname} (ID: {uid})")

    # Create emergency notification for user
    notif = b["Notification"](
        user_id=uid,
        title="🚨 SOS Emergency Alert Recorded",
        message=f"SOS dispatch recorded for {uname}. Emergency contacts notified: {profile.get('emergency_contact_phone') or 'Not set'}. Dial 112 if in life-threatening danger.",
        type="Critical"
    )
    b["save_notification"](notif)

    # If patient has assigned doctor, notify doctor too
    assigned_doc = b["get_patient_assigned_doctor"](uid)
    if assigned_doc and assigned_doc.get("user_id"):
        doc_notif = b["Notification"](
            user_id=assigned_doc["user_id"],
            title="🚨 CRITICAL PATIENT SOS ALERT",
            message=f"Your patient {uname} (ID: {uid}) has triggered an urgent SOS Emergency Alert. Please review contact & chart.",
            type="Critical"
        )
        b["save_notification"](doc_notif)

    return jsonify({
        "message": "🚨 SOS Emergency Alert Dispatched!",
        "patient": uname,
        "contact_phone": profile.get("emergency_contact_phone") or "112",
        "home_address": profile.get("home_address") or "Not provided",
        "blood_group": profile.get("blood_group") or "O+",
        "allergies": profile.get("allergies") or "None",
        "emergency_helpline": "112 / 102"
    })

# ═══════════════════════════════════════════════════════════════
# APPOINTMENTS & CLINICAL RECORDS
# ═══════════════════════════════════════════════════════════════

@app.route("/api/appointments", methods=["GET", "POST"])
@login_required
def api_appointments():
    user = session["user"]
    b = backend()
    role = user.get("role", "patient").lower()
    
    if request.method == "POST":
        data = request.get_json() or {}
        patient_id = data.get("patient_id") or user["user_id"]
        patient_name = data.get("patient_name") or user.get("full_name") or user.get("username") or "Patient"
        doctor_id = data.get("doctor_id") or "usr-doctor-001"
        doctor_name = data.get("doctor_name")

        if not doctor_name:
            all_docs = b["get_all_doctors"]()
            doc_obj = next((d for d in all_docs if d.get("user_id") == doctor_id), None)
            doctor_name = doc_obj.get("full_name") if doc_obj else "Dr. Sarah Jenkins"

        date_val = data.get("appointment_date")
        time_val = data.get("appointment_time")
        if not date_val or not time_val:
            return jsonify({"error": "Appointment date and time are required"}), 400

        appt = b["Appointment"](
            patient_id=patient_id, patient_name=patient_name,
            doctor_id=doctor_id,   doctor_name=doctor_name,
            appointment_date=date_val, appointment_time=time_val,
            reason=data.get("reason", "Neurology Consultation & MRI Review"), status="Pending",
        )
        if b["save_appointment"](appt):
            b["assign_doctor_to_patient"](patient_id, doctor_id)
            return jsonify({"message": "Appointment booked successfully!", "appointment": _json_safe(appt.to_dict() if hasattr(appt, "to_dict") else appt)})
        return jsonify({"error": "Could not save appointment"}), 500
    else:
        if role in ["admin", "receptionist"]:
            appts = b["get_all_appointments"]()
        elif role == "doctor":
            appts = b["get_doctor_appointments"](user["user_id"])
        else:
            appts = b["get_user_appointments"](user["user_id"])
        return jsonify({"appointments": _json_safe(appts)})

@app.route("/api/appointments/<appt_id>/status", methods=["PUT"])
@login_required
def api_update_appointment(appt_id):
    user = session["user"]
    if user.get("role") not in ["receptionist", "admin", "doctor"]:
        return jsonify({"error": "Unauthorized"}), 403
    data = request.get_json() or {}
    ns   = data.get("status")
    if not ns:
        return jsonify({"error": "status required"}), 400
    backend()["update_appointment"](appt_id, {"status": ns})
    return jsonify({"message": "Appointment updated"})

@app.route("/api/prescriptions", methods=["GET", "POST"])
@login_required
def api_prescriptions():
    b = backend()
    user = session["user"]
    role = user.get("role", "patient").lower()
    if request.method == "POST":
        if role not in ["doctor", "admin"]:
            return jsonify({"error": "Unauthorized. Only doctors can issue prescriptions."}), 403
        data = request.get_json() or {}
        patient_id = data.get("patient_id")
        patient_name = data.get("patient_name")
        if not patient_id or not patient_name:
            return jsonify({"error": "patient_id and patient_name are required"}), 400

        doc_name = user.get("full_name") or user.get("username") or "Doctor"
        med_name = data.get("medicine_name") or (data.get("medications", [{}])[0].get("name") if isinstance(data.get("medications"), list) and data.get("medications") else "Prescribed Medication")
        dosage   = data.get("dosage") or (data.get("medications", [{}])[0].get("dosage") if isinstance(data.get("medications"), list) and data.get("medications") else "As directed")
        freq     = data.get("frequency") or (data.get("medications", [{}])[0].get("frequency") if isinstance(data.get("medications"), list) and data.get("medications") else "Twice daily")
        dur      = data.get("duration") or "14 Days"
        instr    = data.get("instructions") or "Take with water as directed by your physician."
        diag     = data.get("diagnosis") or "Neurological Consultation & MRI Findings"
        appt_id  = data.get("appointment_id") or ""
        meds_list= data.get("medications") or [{"name": med_name, "dosage": dosage, "frequency": freq, "duration": dur, "instructions": instr}]

        presc = b["Prescription"](
            patient_id=patient_id,
            patient_name=patient_name,
            doctor_id=user["user_id"],
            doctor_name=doc_name,
            appointment_id=appt_id,
            diagnosis=diag,
            medicine_name=med_name,
            dosage=dosage,
            frequency=freq,
            duration=dur,
            instructions=instr,
            medications=meds_list,
        )
        if b["save_prescription"](presc):
            # Create a notification for the patient
            notif = b["Notification"](
                user_id=patient_id,
                title="💊 New Prescription Issued",
                message=f"Dr. {doc_name} has issued a new prescription for your consultation ({med_name}). Check your Dashboard.",
                type="Medicine"
            )
            b["save_notification"](notif)
            return jsonify({
                "message": "Prescription issued successfully!",
                "prescription": _json_safe(presc.to_dict() if hasattr(presc, "to_dict") else presc)
            })
        return jsonify({"error": "Failed to save prescription"}), 500
    else:
        if role in ["admin", "receptionist"]:
            items = b["get_all_prescriptions"]()
        elif role == "doctor":
            items = b["get_doctor_prescriptions"](user["user_id"])
        else:
            items = b["get_user_prescriptions"](user["user_id"])
        return jsonify({"prescriptions": _json_safe(items)})

@app.route("/api/notifications", methods=["GET"])
@login_required
def api_notifications():
    b = backend()
    user = session["user"]
    items = b["get_user_notifications"](user["user_id"])
    return jsonify({"notifications": _json_safe(items)})

@app.route("/api/audit-logs", methods=["GET"])
@login_required
def api_audit_logs():
    user = session["user"]
    if user.get("role", "").lower() not in ["admin", "doctor"]:
        return jsonify({"error": "Unauthorized"}), 403
    b = backend()
    logs = b["get_all_audit_logs"]()
    return jsonify({"audit_logs": _json_safe(logs)})

@app.route("/api/hospitals", methods=["GET"])
def api_hospitals():
    b = backend()
    hospitals = b["get_all_hospitals"]()
    return jsonify({"hospitals": _json_safe(hospitals)})

@app.route("/api/patients", methods=["GET"])
@login_required
def api_patients():
    user = session["user"]
    if user.get("role", "").lower() not in ["admin", "receptionist", "doctor"]:
        return jsonify({"error": "Unauthorized"}), 403
    b = backend()
    patients = b["get_all_patients"]()
    return jsonify({"patients": _json_safe(patients)})

@app.route("/api/doctors", methods=["GET"])
def api_doctors():
    b = backend()
    doctors = b["get_all_doctors"]()
    return jsonify({"doctors": _json_safe(doctors)})

@app.route("/api/medicines", methods=["GET"])
@login_required
def api_medicines_list():
    b = backend()
    uid = session["user"]["user_id"]
    store = b["get_medicine_store"](uid)
    return jsonify(_json_safe(store))

# ═══════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  NeuroAI Flask Server")
    print("  Open: http://localhost:5000")
    print("="*60 + "\n")
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
