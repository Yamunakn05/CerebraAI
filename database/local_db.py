# database/local_db.py
# ============================================================
# Compatibility layer: Redirects legacy JSON calls to MongoDB Atlas
# ============================================================

from typing import List, Optional, Dict, Any
from database.schema import User, ScanRecord, Hospital, Appointment, Prescription, Notification, ModelVersion, Payment
import database.mongo_db as mongo_db

def clear_database_cache() -> None:
    """No-op for MongoDB backend."""
    pass

# ── User Operations ────────────────────────────────────────
def get_all_users() -> List[Dict]:
    return mongo_db.get_all_users()

def find_user_by_email(email: str) -> Optional[Dict]:
    return mongo_db.find_user_by_email(email)

def find_user_by_id(user_id: str) -> Optional[Dict]:
    return mongo_db.find_user_by_id(user_id)

def find_user_by_username(username: str) -> Optional[Dict]:
    return mongo_db.find_user_by_username(username)

def create_user(user: User) -> bool:
    return mongo_db.create_user(user)

def update_user(user_id: str, updates: Dict[str, Any]) -> bool:
    return mongo_db.update_user(user_id, updates)

def get_all_patients() -> List[Dict]:
    return [u for u in get_all_users() if u.get("role") == "patient"]

def get_user_emergency_profile(user_id: str) -> Dict[str, Any]:
    return mongo_db.get_user_emergency_profile(user_id)

def update_user_emergency_profile(user_id: str, profile_data: Dict[str, Any]) -> bool:
    return mongo_db.update_user_emergency_profile(user_id, profile_data)

def get_all_doctors() -> List[Dict]:
    return [u for u in get_all_users() if u.get("role") == "doctor"]

def get_users_by_role(role: str) -> List[Dict]:
    target = (role or "").lower()
    return [u for u in get_all_users() if (u.get("role") or "").lower() == target]

def get_all_admins() -> List[Dict]:
    return get_users_by_role("admin")

def get_all_receptionists() -> List[Dict]:
    return get_users_by_role("receptionist")

def get_all_radiologists() -> List[Dict]:
    return get_users_by_role("radiologist")

# ── Scan Record Operations ─────────────────────────────────
def get_all_scans() -> List[Dict]:
    return mongo_db.get_all_scans()

def get_user_scans(user_id: str) -> List[Dict]:
    return mongo_db.get_user_scans(user_id)

def get_scan_by_id(scan_id: str) -> Optional[Dict]:
    return mongo_db.get_scan_by_id(scan_id)

def save_scan_record(scan: ScanRecord) -> bool:
    return mongo_db.save_scan_record(scan)

def update_scan_record(scan_id: str, updates: Dict[str, Any]) -> bool:
    return mongo_db.update_scan_record(scan_id, updates)

def delete_scan_record(scan_id: str) -> bool:
    return mongo_db.delete_scan_record(scan_id)

def get_recent_scans(limit: int = 10) -> List[Dict]:
    return mongo_db.get_recent_scans(limit)

# ── Doctor-Patient Links ────────────────────────────────────
def link_doctor_patient(doctor_id: str, patient_id: str, status: str = "Pending") -> bool:
    return mongo_db.link_doctor_patient(doctor_id, patient_id, status)

def get_doctor_patient_links(doctor_id: str) -> List[Dict]:
    return mongo_db.get_doctor_patient_links(doctor_id)

def get_doctor_patients(doctor_id: str) -> List[Dict]:
    links = get_doctor_patient_links(doctor_id)
    patient_ids = [l["patient_id"] for l in links]
    all_users = get_all_users()
    return [u for u in all_users if u.get("user_id") in patient_ids]

def get_doctor_assigned_patients(doctor_id: str) -> List[Dict]:
    return mongo_db.get_doctor_assigned_patients(doctor_id)

def get_assigned_patients_for_doctor(doctor_id: str) -> List[Dict]:
    return mongo_db.get_doctor_assigned_patients(doctor_id)

def get_patient_scans_for_doctor(doctor_id: str) -> List[Dict]:
    return mongo_db.get_patient_scans_for_doctor(doctor_id)

def assign_doctor_to_patient(patient_id: str, doctor_id: str) -> bool:
    return mongo_db.assign_doctor_to_patient(patient_id, doctor_id)

def get_patient_assigned_doctor(patient_id: str) -> Optional[Dict]:
    return mongo_db.get_patient_assigned_doctor(patient_id)

# ── Statistics ─────────────────────────────────────────────
def get_platform_stats() -> Dict[str, Any]:
    users = get_all_users()
    scans = get_all_scans()
    appts = get_all_appointments()
    prescs = get_all_prescriptions()
    return {
        "total_users": len(users),
        "total_patients": sum(1 for u in users if u.get("role") == "patient"),
        "total_doctors": sum(1 for u in users if u.get("role") == "doctor"),
        "total_radiologists": sum(1 for u in users if u.get("role") == "radiologist"),
        "total_receptionists": sum(1 for u in users if u.get("role") == "receptionist"),
        "total_scans": len(scans),
        "tumors_detected": sum(1 for s in scans if s.get("has_tumor")),
        "critical_cases": sum(1 for s in scans if s.get("severity_level") == "Critical"),
        "total_appointments": len(appts),
        "total_prescriptions": len(prescs),
    }

# ── Hospital Operations ────────────────────────────────────
def get_all_hospitals() -> List[Dict]:
    return mongo_db.get_all_hospitals()

def save_hospital(hospital: Hospital) -> bool:
    return mongo_db.save_hospital(hospital)

# ── Appointment Operations ─────────────────────────────────
def get_all_appointments() -> List[Dict]:
    return mongo_db.get_all_appointments()

def get_user_appointments(user_id: str) -> List[Dict]:
    return mongo_db.get_user_appointments(user_id)

def get_doctor_appointments(doctor_id: str) -> List[Dict]:
    return mongo_db.get_doctor_appointments(doctor_id)

def save_appointment(appt: Appointment) -> bool:
    return mongo_db.save_appointment(appt)

def update_appointment(appt_id: str, updates: Dict[str, Any]) -> bool:
    return mongo_db.update_appointment(appt_id, updates)

# ── Prescription Operations ────────────────────────────────
def get_all_prescriptions() -> List[Dict]:
    return mongo_db.get_all_prescriptions()

def get_user_prescriptions(user_id: str) -> List[Dict]:
    return mongo_db.get_user_prescriptions(user_id)

def get_doctor_prescriptions(doctor_id: str) -> List[Dict]:
    return mongo_db.get_doctor_prescriptions(doctor_id)

def save_prescription(presc: Prescription) -> bool:
    return mongo_db.save_prescription(presc)

# ── Notification Operations ────────────────────────────────
def get_all_notifications() -> List[Dict]:
    return mongo_db.get_all_notifications()

def get_user_notifications(user_id: str) -> List[Dict]:
    return mongo_db.get_user_notifications(user_id)

def save_notification(notif: Notification) -> bool:
    return mongo_db.save_notification(notif)

def mark_notification_read(notif_id: str) -> bool:
    return mongo_db.mark_notification_read(notif_id)

# ── Model Version Operations ───────────────────────────────
def get_all_model_versions() -> List[Dict]:
    return mongo_db.get_all_model_versions()

def save_model_version(model: ModelVersion) -> bool:
    return mongo_db.save_model_version(model)

def set_active_model(model_id: str) -> bool:
    return mongo_db.set_active_model(model_id)

# ── Payment Operations ─────────────────────────────────────
def get_all_payments() -> List[Dict]:
    return mongo_db.get_all_payments()

def get_user_payments(user_id: str) -> List[Dict]:
    return mongo_db.get_user_payments(user_id)

def save_payment(pay: Payment) -> bool:
    return mongo_db.save_payment(pay)

def update_payment(pay_id: str, updates: Dict[str, Any]) -> bool:
    return mongo_db.update_payment(pay_id, updates)

# ── Audit Logging Operations ────────────────────────────────
def get_all_audit_logs() -> List[Dict]:
    return mongo_db.get_all_audit_logs()

def log_audit_event(username: str, action: str, details: str) -> None:
    mongo_db.log_audit_event(username, action, details)

def get_audit_logs() -> List[Dict]:
    return mongo_db.get_all_audit_logs()

# ── Medicine Intelligence Operations ─────────────────────────
def get_medicine_store(user_id: str) -> Dict[str, Any]:
    return mongo_db.get_medicine_store(user_id)

def update_medicine_recent(user_id: str, medicine_name: str) -> None:
    mongo_db.update_medicine_recent(user_id, medicine_name)

def toggle_medicine_favorite(user_id: str, medicine_name: str) -> bool:
    return mongo_db.toggle_medicine_favorite(user_id, medicine_name)

def bootstrap_demo_data() -> bool:
    """This function is maintained for backward compatibility. Demo seeding handled by migration scripts."""
    return True
