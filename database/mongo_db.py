"""MongoDB repository for CerebraAI with automatic local fallback when cloud DB is unavailable.
"""
import os
import json
import re
import uuid
import bcrypt
from datetime import datetime
from typing import Any, Dict, List, Optional

from pymongo import DESCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from gridfs import GridFS

from database.mongo_config import MongoConfigurationError, get_database, get_users_collection
from database.schema import User, ScanRecord, Hospital, Appointment, Prescription, Notification, ModelVersion, Payment


# ── In-Memory Datastore Fallback ──────────────────────────────
_DEMO_HASH = bcrypt.hashpw(b"Password123!", bcrypt.gensalt(10)).decode("utf-8")
_LOCAL_STORE: Dict[str, Any] = {
    "users": [],
    "scans": [],
    "hospitals": [],
    "appointments": [],
    "prescriptions": [],
    "notifications": [],
    "payments": [],
    "doctor_links": [],
    "model_versions": [],
    "audit_logs": [],
    "medicine_intelligence": {},
    "gridfs_files": {},
}

_DB_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "local_store_db.json")

def _save_local_store_to_disk():
    # Local disk persistence disabled as requested; all data lives in MongoDB Atlas.
    pass

def _load_local_store_from_disk():
    pass

def _clean(doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if doc is None:
        return None
    result = dict(doc)
    result.pop("_id", None)
    return result


def _all(collection: str, query: Optional[Dict[str, Any]] = None, sort=None, limit: int = 0) -> List[Dict]:
    try:
        cursor = get_database()[collection].find(query or {})
        if sort:
            cursor = cursor.sort(*sort)
        if limit:
            cursor = cursor.limit(limit)
        docs = [_clean(item) for item in cursor]
        if docs:
            return docs
    except (MongoConfigurationError, PyMongoError, Exception):
        pass

    items = _LOCAL_STORE.get(collection, [])
    if query:
        filtered = []
        for item in items:
            match = True
            for k, v in query.items():
                if item.get(k) != v:
                    match = False
                    break
            if match:
                filtered.append(item)
        items = filtered
    if sort:
        key, direction = sort
        items = sorted(items, key=lambda x: x.get(key, ""), reverse=(direction == DESCENDING))
    if limit:
        items = items[:limit]
    return [_clean(item) for item in items]


def _insert(collection: str, value: Any) -> bool:
    data = value.to_dict() if hasattr(value, "to_dict") else dict(value)
    # Sync in-memory fallback list if needed
    store_list = _LOCAL_STORE.setdefault(collection, [])
    item_id = data.get("scan_id") or data.get("appointment_id") or data.get("user_id")
    if not item_id or not any((item.get("scan_id") or item.get("appointment_id") or item.get("user_id")) == item_id for item in store_list if isinstance(item, dict)):
        store_list.append(data)

    try:
        get_database()[collection].insert_one(data)
    except (MongoConfigurationError, PyMongoError, Exception):
        pass
    return True


def _update(collection: str, key: str, value: str, updates: Dict[str, Any]) -> bool:
    items = _LOCAL_STORE.get(collection, [])
    for item in items:
        if isinstance(item, dict) and item.get(key) == value:
            item.update(updates)

    try:
        get_database()[collection].update_one({key: value}, {"$set": updates})
        return True
    except (MongoConfigurationError, PyMongoError, Exception):
        return True


def _case_query(field: str, value: str) -> Dict[str, Any]:
    return {field: {"$regex": f"^{re.escape(value)}$", "$options": "i"}}


def get_all_users() -> List[Dict]:
    return _all("users")


def find_user_by_email(email: str) -> Optional[Dict]:
    value = (email or "").strip()
    if not value:
        return None
    try:
        coll = get_users_collection()
        user = coll.find_one({"email": value.lower()}) or coll.find_one({"email": value}) or coll.find_one(_case_query("email", value))
        return _clean(user)
    except (MongoConfigurationError, PyMongoError, Exception):
        for u in _LOCAL_STORE["users"]:
            if u.get("email", "").lower() == value.lower():
                return _clean(u)
        return None


def find_user_by_username(username: str) -> Optional[Dict]:
    value = (username or "").strip()
    if not value:
        return None
    try:
        coll = get_users_collection()
        user = coll.find_one({"username": value}) or coll.find_one({"username": value.lower()}) or coll.find_one(_case_query("username", value))
        return _clean(user)
    except (MongoConfigurationError, PyMongoError, Exception):
        for u in _LOCAL_STORE["users"]:
            if u.get("username", "").lower() == value.lower():
                return _clean(u)
        return None


def find_user_by_id(user_id: str) -> Optional[Dict]:
    try:
        return _clean(get_users_collection().find_one({"user_id": user_id}))
    except (MongoConfigurationError, PyMongoError, Exception):
        for u in _LOCAL_STORE["users"]:
            if u.get("user_id") == user_id:
                return _clean(u)
        return None


def create_user(user: User) -> bool:
    try:
        get_users_collection().insert_one(user.to_dict())
        return True
    except DuplicateKeyError:
        return False
    except (MongoConfigurationError, PyMongoError, Exception):
        if find_user_by_email(user.email) or find_user_by_username(user.username):
            return False
        _LOCAL_STORE["users"].append(user.to_dict())
        return True


def update_user(user_id: str, updates: Dict[str, Any]) -> bool:
    return _update("users", "user_id", user_id, updates)


def get_user_emergency_profile(user_id: str) -> Dict[str, Any]:
    u = find_user_by_id(user_id) or {}
    return {
        "user_id": user_id,
        "full_name": u.get("full_name") or u.get("username", "Patient"),
        "phone": u.get("phone", ""),
        "blood_group": u.get("blood_group", "O+"),
        "allergies": u.get("allergies", "None"),
        "surgeries": u.get("surgeries", "None"),
        "emergency_contact_name": u.get("emergency_contact_name", ""),
        "emergency_contact_phone": u.get("emergency_contact_phone", ""),
        "emergency_contact_relation": u.get("emergency_contact_relation", "Family / Guardian"),
        "home_address": u.get("home_address", ""),
        "medical_alert_notes": u.get("medical_alert_notes", ""),
    }


def update_user_emergency_profile(user_id: str, profile_data: Dict[str, Any]) -> bool:
    allowed = {
        "emergency_contact_name", "emergency_contact_phone", "emergency_contact_relation",
        "home_address", "medical_alert_notes", "blood_group", "allergies", "phone"
    }
    updates = {k: str(v).strip() for k, v in profile_data.items() if k in allowed and v is not None}
    return update_user(user_id, updates)


def get_all_scans() -> List[Dict]:
    return _all("scans", sort=("scan_date", DESCENDING))


def get_user_scans(user_id: str) -> List[Dict]:
    return _all("scans", {"user_id": user_id}, ("scan_date", DESCENDING))


def get_scan_by_id(scan_id: str) -> Optional[Dict]:
    try:
        return _clean(get_database()["scans"].find_one({"scan_id": scan_id}))
    except (MongoConfigurationError, PyMongoError, Exception):
        for s in _LOCAL_STORE["scans"]:
            if s.get("scan_id") == scan_id:
                return _clean(s)
        return None


def save_scan_record(scan: ScanRecord) -> bool:
    return _insert("scans", scan)


def update_scan_record(scan_id: str, updates: Dict[str, Any]) -> bool:
    return _update("scans", "scan_id", scan_id, updates)


def delete_scan_record(scan_id: str) -> bool:
    try:
        db = get_database()
        record = db["scans"].find_one({"scan_id": scan_id})
        if record and record.get("image_file_id"):
            GridFS(db).delete(record["image_file_id"])
        return db["scans"].delete_one({"scan_id": scan_id}).deleted_count == 1
    except (MongoConfigurationError, PyMongoError, Exception):
        _LOCAL_STORE["scans"] = [s for s in _LOCAL_STORE["scans"] if s.get("scan_id") != scan_id]
        return True


def get_recent_scans(limit: int = 10) -> List[Dict]:
    return _all("scans", sort=("scan_date", DESCENDING), limit=limit)


def store_scan_file(user_id: str, scan_id: str, filename: str, content: bytes, content_type: str) -> Any:
    """Store original scan bytes in MongoDB GridFS or local fallback."""
    try:
        return GridFS(get_database()).put(
            content, filename=filename, user_id=user_id, scan_id=scan_id,
            content_type=content_type, uploaded_at=datetime.utcnow()
        )
    except (MongoConfigurationError, PyMongoError, Exception):
        file_id = f"local-file-{uuid.uuid4().hex[:8]}"
        _LOCAL_STORE["gridfs_files"][file_id] = content
        return file_id


def read_scan_file(user_id: str, scan_id: str) -> Optional[bytes]:
    try:
        record = get_database()["scans"].find_one({"scan_id": scan_id, "user_id": user_id})
        if not record or not record.get("image_file_id"):
            return None
        return GridFS(get_database()).get(record["image_file_id"]).read()
    except (MongoConfigurationError, PyMongoError, Exception):
        for s in _LOCAL_STORE["scans"]:
            if s.get("scan_id") == scan_id and s.get("user_id") == user_id:
                fid = s.get("image_file_id")
                return _LOCAL_STORE["gridfs_files"].get(fid)
        return None


def get_all_hospitals() -> List[Dict]:
    return _all("hospitals")


def save_hospital(item: Hospital) -> bool:
    return _insert("hospitals", item)





def get_all_prescriptions() -> List[Dict]:
    return _all("prescriptions")


def get_user_prescriptions(user_id: str) -> List[Dict]:
    return _all("prescriptions", {"patient_id": user_id})


def get_doctor_prescriptions(user_id: str) -> List[Dict]:
    return _all("prescriptions", {"doctor_id": user_id})


def save_prescription(item: Prescription) -> bool:
    return _insert("prescriptions", item)


def get_all_notifications() -> List[Dict]:
    return _all("notifications")


def get_user_notifications(user_id: str) -> List[Dict]:
    return _all("notifications", {"user_id": user_id})


def save_notification(item: Notification) -> bool:
    return _insert("notifications", item)


def mark_notification_read(item_id: str) -> bool:
    return _update("notifications", "notification_id", item_id, {"is_read": True})


def get_all_payments() -> List[Dict]:
    return _all("payments")


def get_user_payments(user_id: str) -> List[Dict]:
    return _all("payments", {"patient_id": user_id})


def save_payment(item: Payment) -> bool:
    return _insert("payments", item)


def update_payment(item_id: str, updates: Dict[str, Any]) -> bool:
    return _update("payments", "payment_id", item_id, updates)


def link_doctor_patient(doctor_id: str, patient_id: str, status: str = "Pending") -> bool:
    try:
        get_database()["doctor_links"].update_one(
            {"doctor_id": doctor_id, "patient_id": patient_id},
            {"$set": {"status": status, "linked_at": datetime.utcnow().isoformat()}},
            upsert=True
        )
        return True
    except (MongoConfigurationError, PyMongoError, Exception):
        _LOCAL_STORE["doctor_links"].append({
            "doctor_id": doctor_id, "patient_id": patient_id,
            "status": status, "linked_at": datetime.utcnow().isoformat()
        })
        return True


def get_doctor_patient_links(doctor_id: str) -> List[Dict]:
    return _all("doctor_links", {"doctor_id": doctor_id})


def assign_doctor_to_patient(patient_id: str, doctor_id: str) -> bool:
    """Link a patient to a doctor and mark link as Active."""
    link_doctor_patient(doctor_id, patient_id, status="Active")
    try:
        get_database()["users"].update_one(
            {"user_id": patient_id},
            {"$set": {"assigned_doctor_id": doctor_id}}
        )
    except Exception:
        for u in _LOCAL_STORE["users"]:
            if u.get("user_id") == patient_id:
                u["assigned_doctor_id"] = doctor_id
    return True


def get_patient_assigned_doctor(patient_id: str) -> Optional[Dict]:
    """Get the doctor assigned to or selected by a patient."""
    try:
        user = get_database()["users"].find_one({"user_id": patient_id})
        if user and user.get("assigned_doctor_id"):
            doc = get_database()["users"].find_one({"user_id": user["assigned_doctor_id"]})
            if doc:
                return _clean(doc)
        # Check active link
        link = get_database()["doctor_links"].find_one({"patient_id": patient_id, "status": "Active"})
        if link:
            doc = get_database()["users"].find_one({"user_id": link["doctor_id"]})
            if doc:
                return _clean(doc)
        # Check latest appointment
        appt = get_database()["appointments"].find_one({"patient_id": patient_id}, sort=[("appointment_date", DESCENDING)])
        if appt and appt.get("doctor_id"):
            doc = get_database()["users"].find_one({"user_id": appt["doctor_id"]})
            if doc:
                return _clean(doc)
    except Exception:
        pass

    for u in _LOCAL_STORE["users"]:
        if u.get("user_id") == patient_id and u.get("assigned_doctor_id"):
            doc_id = u["assigned_doctor_id"]
            return next((_clean(x) for x in _LOCAL_STORE["users"] if x.get("user_id") == doc_id), None)
    for l in _LOCAL_STORE["doctor_links"]:
        if l.get("patient_id") == patient_id:
            doc_id = l.get("doctor_id")
            return next((_clean(x) for x in _LOCAL_STORE["users"] if x.get("user_id") == doc_id), None)
    return None


def get_doctor_assigned_patients(doctor_id: str) -> List[Dict]:
    """Get full profile list of patients who selected or booked with this doctor."""
    patient_ids = set()
    # 1. From doctor_links
    for link in get_doctor_patient_links(doctor_id):
        if link.get("patient_id"):
            patient_ids.add(link["patient_id"])
    # 2. From appointments
    for appt in get_doctor_appointments(doctor_id):
        if appt.get("patient_id"):
            patient_ids.add(appt["patient_id"])
    # 3. From users table with assigned_doctor_id
    try:
        for u in get_database()["users"].find({"assigned_doctor_id": doctor_id}):
            if u.get("user_id"):
                patient_ids.add(u["user_id"])
    except Exception:
        for u in _LOCAL_STORE["users"]:
            if u.get("assigned_doctor_id") == doctor_id and u.get("user_id"):
                patient_ids.add(u["user_id"])

    all_users = get_all_users()
    all_scans = get_all_scans()
    assigned = []
    for u in all_users:
        if u.get("user_id") in patient_ids and u.get("role") == "patient":
            u_clean = dict(u)
            u_clean["scan_count"] = sum(1 for s in all_scans if s.get("user_id") == u.get("user_id"))
            assigned.append(u_clean)
    return assigned


def get_patient_scans_for_doctor(doctor_id: str) -> List[Dict]:
    """Return only scans for patients who selected or booked with this doctor."""
    assigned_patients = get_doctor_assigned_patients(doctor_id)
    allowed_uids = set(p.get("user_id") for p in assigned_patients if p.get("user_id"))
    all_scans = get_all_scans()
    return [s for s in all_scans if s.get("user_id") in allowed_uids or s.get("doctor_id") == doctor_id]


def accept_patient_assignment(doctor_id: str, patient_id: str) -> bool:
    try:
        return get_database()["doctor_links"].update_one(
            {"doctor_id": doctor_id, "patient_id": patient_id},
            {"$set": {"status": "Active"}}
        ).matched_count == 1
    except (MongoConfigurationError, PyMongoError, Exception):
        for link in _LOCAL_STORE["doctor_links"]:
            if link.get("doctor_id") == doctor_id and link.get("patient_id") == patient_id:
                link["status"] = "Active"
                return True
        return False


def get_all_appointments() -> List[Dict]:
    return _all("appointments", sort=("created_at", DESCENDING))

def get_user_appointments(user_id: str) -> List[Dict]:
    return _all("appointments", {"patient_id": user_id}, sort=("appointment_date", DESCENDING))

def get_doctor_appointments(doctor_id: str) -> List[Dict]:
    return _all("appointments", {"doctor_id": doctor_id}, sort=("appointment_date", DESCENDING))

def save_appointment(appt: Any) -> bool:
    return _insert("appointments", appt)

def update_appointment(appt_id: str, updates: Dict[str, Any]) -> bool:
    return _update("appointments", "appointment_id", appt_id, updates)

def get_all_prescriptions() -> List[Dict]:
    return _all("prescriptions", sort=("created_at", DESCENDING))

def get_user_prescriptions(user_id: str) -> List[Dict]:
    return _all("prescriptions", {"patient_id": user_id}, sort=("created_at", DESCENDING))

def get_doctor_prescriptions(doctor_id: str) -> List[Dict]:
    return _all("prescriptions", {"doctor_id": doctor_id}, sort=("created_at", DESCENDING))

def save_prescription(presc: Any) -> bool:
    return _insert("prescriptions", presc)

def get_all_notifications() -> List[Dict]:
    return _all("notifications", sort=("created_at", DESCENDING))

def get_user_notifications(user_id: str) -> List[Dict]:
    return _all("notifications", {"user_id": user_id}, sort=("created_at", DESCENDING))

def save_notification(notif: Any) -> bool:
    return _insert("notifications", notif)

def mark_notification_read(notif_id: str) -> bool:
    return _update("notifications", "notification_id", notif_id, {"is_read": True})

def get_all_payments() -> List[Dict]:
    return _all("payments", sort=("created_at", DESCENDING))

def get_user_payments(user_id: str) -> List[Dict]:
    return _all("payments", {"patient_id": user_id}, sort=("created_at", DESCENDING))

def save_payment(pay: Any) -> bool:
    return _insert("payments", pay)

def update_payment(pay_id: str, updates: Dict[str, Any]) -> bool:
    return _update("payments", "payment_id", pay_id, updates)


def get_all_model_versions() -> List[Dict]:
    return _all("model_versions")


def save_model_version(item: ModelVersion) -> bool:
    return _insert("model_versions", item)


def set_active_model(item_id: str) -> bool:
    try:
        collection = get_database()["model_versions"]
        collection.update_many({}, {"$set": {"is_active": False}})
        return collection.update_one({"version_id": item_id}, {"$set": {"is_active": True}}).matched_count == 1
    except (MongoConfigurationError, PyMongoError, Exception):
        for m in _LOCAL_STORE["model_versions"]:
            m["is_active"] = (m.get("version_id") == item_id)
        return True


def get_all_audit_logs() -> List[Dict]:
    return _all("audit_logs", sort=("timestamp", DESCENDING))


def log_audit_event(username: str, action: str, details: str) -> None:
    entry = {"timestamp": datetime.utcnow().isoformat(), "username": username, "action": action, "details": details}
    try:
        get_database()["audit_logs"].insert_one(entry)
    except (MongoConfigurationError, PyMongoError, Exception):
        _LOCAL_STORE["audit_logs"].append(entry)


def get_medicine_store(user_id: str) -> Dict[str, Any]:
    try:
        item = get_database()["medicine_intelligence"].find_one({"user_id": user_id}) or {}
        return {"favorites": item.get("favorites", []), "recent": item.get("recent", [])}
    except (MongoConfigurationError, PyMongoError, Exception):
        item = _LOCAL_STORE["medicine_intelligence"].get(user_id, {})
        return {"favorites": item.get("favorites", []), "recent": item.get("recent", [])}


def update_medicine_recent(user_id: str, medicine_name: str) -> None:
    try:
        store = get_medicine_store(user_id)
        recent = [x for x in store["recent"] if x.lower() != medicine_name.lower()]
        get_database()["medicine_intelligence"].update_one(
            {"user_id": user_id},
            {"$set": {"recent": [medicine_name] + recent[:9], "favorites": store["favorites"]}},
            upsert=True
        )
    except (MongoConfigurationError, PyMongoError, Exception):
        store = get_medicine_store(user_id)
        recent = [x for x in store["recent"] if x.lower() != medicine_name.lower()]
        _LOCAL_STORE["medicine_intelligence"][user_id] = {
            "recent": [medicine_name] + recent[:9],
            "favorites": store["favorites"]
        }


def toggle_medicine_favorite(user_id: str, medicine_name: str) -> bool:
    store = get_medicine_store(user_id)
    existing = next((x for x in store["favorites"] if x.lower() == medicine_name.lower()), None)
    favorites = [x for x in store["favorites"] if x.lower() != medicine_name.lower()] if existing else [medicine_name] + store["favorites"][:24]
    try:
        get_database()["medicine_intelligence"].update_one(
            {"user_id": user_id},
            {"$set": {"favorites": favorites, "recent": store["recent"]}},
            upsert=True
        )
    except (MongoConfigurationError, PyMongoError, Exception):
        _LOCAL_STORE["medicine_intelligence"][user_id] = {
            "favorites": favorites,
            "recent": store["recent"]
        }
    return not bool(existing)
