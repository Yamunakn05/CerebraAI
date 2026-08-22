# database/mongo_config.py
# ============================================================
# MongoDB Atlas connection configuration for BrainTumorAI
# ============================================================

import os
from typing import Optional

from dotenv import load_dotenv

try:
    from pymongo import ASCENDING, MongoClient
    from pymongo.collection import Collection
    from pymongo.database import Database
    from pymongo.errors import PyMongoError
    from pymongo.collation import Collation
except ImportError:  # Allows the app to fail gracefully until pymongo is installed.
    ASCENDING = 1
    MongoClient = None
    Collection = object
    Database = object
    PyMongoError = Exception
    Collation = None


_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(_ROOT, ".env"))

DB_NAME = "BrainTumorAI"
MONGODB_URI = os.getenv("MONGODB_URI", "").strip()

_client: Optional[MongoClient] = None
_db: Optional[Database] = None
_users: Optional[Collection] = None
_connection_error: Optional[str] = None


_last_failure_time: float = 0.0
CIRCUIT_BREAKER_COOLDOWN: float = 30.0


class MongoConfigurationError(RuntimeError):
    """Raised when MongoDB cannot be configured or reached."""


def _set_connection_error(message: str) -> None:
    global _connection_error, _last_failure_time
    _connection_error = message
    if message:
        import time
        _last_failure_time = time.time()


def get_connection_error() -> Optional[str]:
    return _connection_error


def get_client() -> MongoClient:
    """Return a connected MongoDB client, validating the connection lazily."""
    global _client, _last_failure_time

    if MongoClient is None:
        message = "pymongo is not installed. Install project requirements before using MongoDB authentication."
        _set_connection_error(message)
        raise MongoConfigurationError(message)

    if not MONGODB_URI:
        message = "MONGODB_URI is not configured in .env."
        _set_connection_error(message)
        raise MongoConfigurationError(message)

    import time
    now = time.time()
    if _client is None and _connection_error and (now - _last_failure_time < CIRCUIT_BREAKER_COOLDOWN):
        raise MongoConfigurationError(f"MongoDB connection circuit breaker active: {_connection_error}")

    if _client is None:
        try:
            _client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=1500)
            _client.admin.command("ping")
            _set_connection_error("")
        except PyMongoError as exc:
            _client = None
            message = f"MongoDB connection failed: {exc}"
            _set_connection_error(message)
            raise MongoConfigurationError(message) from exc

    return _client


def get_database() -> Database:
    """Return the BrainTumorAI database."""
    global _db
    if _db is None:
        _db = get_client()[DB_NAME]
    return _db


def get_users_collection() -> Collection:
    """Return the users collection and ensure required indexes exist."""
    global _users
    if _users is None:
        _users = get_database()["users"]
        ensure_indexes(_users)
    return _users


_indexes_created = False

def ensure_indexes(users_collection: Optional[Collection] = None) -> None:
    """Create unique indexes required by authentication and application data."""
    global _indexes_created
    if _indexes_created:
        return
    db = get_database()
    try:
        kwargs = {}
        if Collation is not None:
            kwargs["collation"] = Collation(locale="en", strength=2)
        
        # Users
        users_coll = users_collection if users_collection is not None else db["users"]
        users_coll.create_index([("email", ASCENDING)], unique=True, name="uniq_users_email", **kwargs)
        users_coll.create_index([("username", ASCENDING)], unique=True, name="uniq_users_username", **kwargs)
        users_coll.create_index([("user_id", ASCENDING)], unique=True, name="uniq_users_id")

        # Scans
        db["scans"].create_index([("scan_id", ASCENDING)], unique=True, name="uniq_scan_id")
        db["scans"].create_index([("user_id", ASCENDING), ("scan_date", ASCENDING)], name="idx_scan_user_date")

        # Appointments
        db["appointments"].create_index([("appointment_id", ASCENDING)], unique=True, name="uniq_appt_id")
        db["appointments"].create_index([("patient_id", ASCENDING)], name="idx_appt_patient")
        db["appointments"].create_index([("doctor_id", ASCENDING)], name="idx_appt_doctor")

        # Prescriptions
        db["prescriptions"].create_index([("prescription_id", ASCENDING)], unique=True, name="uniq_presc_id")
        db["prescriptions"].create_index([("patient_id", ASCENDING)], name="idx_presc_patient")

        # Notifications
        db["notifications"].create_index([("notification_id", ASCENDING)], unique=True, name="uniq_notif_id")
        db["notifications"].create_index([("user_id", ASCENDING)], name="idx_notif_user")

        # Payments
        db["payments"].create_index([("payment_id", ASCENDING)], unique=True, name="uniq_pay_id")
        db["payments"].create_index([("patient_id", ASCENDING)], name="idx_pay_patient")

        # Hospitals
        db["hospitals"].create_index([("hospital_id", ASCENDING)], unique=True, name="uniq_hosp_id")

        # Doctor Links
        db["doctor_links"].create_index([("doctor_id", ASCENDING), ("patient_id", ASCENDING)], unique=True, name="uniq_link_doc_pat")

        # Model Versions
        db["model_versions"].create_index([("version_id", ASCENDING)], unique=True, name="uniq_model_ver_id")

        # Audit Logs
        db["audit_logs"].create_index([("timestamp", ASCENDING)], name="idx_audit_time")

        # Medicine Intelligence
        db["medicine_intelligence"].create_index([("user_id", ASCENDING)], unique=True, name="uniq_med_intel_user")

        _indexes_created = True
    except PyMongoError as exc:
        message = f"MongoDB index creation failed: {exc}"
        _set_connection_error(message)
        raise MongoConfigurationError(message) from exc


class _CollectionProxy:
    """Lazy collection proxy so imports do not fail when MongoDB is unavailable."""

    def __getattr__(self, name: str):
        return getattr(get_users_collection(), name)


# Exposed collection handle requested by the migration task.
users = _CollectionProxy()
