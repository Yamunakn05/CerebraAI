# database/schema.py
# ============================================================
# Data Models (Dataclasses) for the BrainTumorAI platform
# ============================================================

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid


@dataclass
class User:
    user_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8].upper())
    username: str = ""
    email: str = ""
    password_hash: str = ""
    role: str = "patient"          # "patient" | "doctor"
    full_name: str = ""
    age: Optional[int] = None
    gender: str = ""
    phone: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_login: str = ""
    language: str = "en"
    accessibility_mode: bool = False
    high_contrast: bool = False
    font_size: str = "medium"      # "small" | "medium" | "large"
    
    # Clinical Demographics Metadata
    weight: float = 70.0
    blood_group: str = "O+"
    allergies: str = "None"
    surgeries: str = "None"
    assigned_doctor_id: str = ""

    # Emergency Contact & Location Profile
    emergency_contact_name: str = ""
    emergency_contact_phone: str = ""
    emergency_contact_relation: str = "Family / Guardian"
    home_address: str = ""
    medical_alert_notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "User":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class ScanRecord:
    scan_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12].upper())
    user_id: str = ""
    patient_name: str = ""
    scan_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    filename: str = ""
    scan_path: str = ""

    # Classification
    tumor_type: str = ""
    confidence: float = 0.0
    has_tumor: bool = False

    # Segmentation
    tumor_area_pct: float = 0.0
    tumor_area_px: int = 0

    # Brain region
    brain_region: str = ""

    # Severity
    severity_level: str = ""
    severity_score: int = 0

    # Quality
    quality_score: int = 0
    quality_grade: str = ""

    # Report & Approval Workflow Status
    report_path: str = ""
    notes: str = ""
    status: str = "Pending AI Analysis"  # "Pending AI Analysis" | "Pending Doctor Review" | "Approved" | "Rejected" | "Requires Additional Tests"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ScanRecord":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

    def get_summary(self) -> str:
        if self.has_tumor:
            return (
                f"{self.tumor_type.capitalize()} detected | "
                f"{self.confidence:.0f}% confidence | "
                f"Severity: {self.severity_level}"
            )
        return f"No tumor detected | {self.confidence:.0f}% confidence"


@dataclass
class DoctorPatientLink:
    doctor_id: str = ""
    patient_id: str = ""
    linked_at: str = field(default_factory=lambda: datetime.now().isoformat())
    notes: str = ""
    status: str = "Pending"  # "Pending" | "Active" | "Transferred"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Hospital:
    hospital_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8].upper())
    name: str = ""
    location: str = ""
    contact: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Hospital":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class Appointment:
    appointment_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8].upper())
    patient_id: str = ""
    patient_name: str = ""
    doctor_id: str = ""
    doctor_name: str = ""
    appointment_date: str = ""
    appointment_time: str = ""
    reason: str = ""
    status: str = "Pending"  # "Pending" | "Approved" | "Rejected" | "Completed"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Appointment":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class Prescription:
    prescription_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8].upper())
    patient_id: str = ""
    patient_name: str = ""
    doctor_id: str = ""
    doctor_name: str = ""
    appointment_id: str = ""
    scan_id: str = ""
    diagnosis: str = ""
    medicine_name: str = ""
    dosage: str = ""
    frequency: str = ""
    duration: str = ""
    instructions: str = ""
    medications: List[Dict[str, Any]] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Prescription":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class Notification:
    notification_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8].upper())
    user_id: str = ""
    title: str = ""
    message: str = ""
    is_read: bool = False
    type: str = "General"  # "Appointment" | "Medicine" | "Report" | "Critical" | "Follow-up" | "General"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Notification":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class ModelVersion:
    version_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8].upper())
    version_name: str = ""
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    training_date: str = field(default_factory=lambda: datetime.now().isoformat()[:10])
    is_active: bool = False
    size_mb: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ModelVersion":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class Payment:
    payment_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8].upper())
    patient_id: str = ""
    patient_name: str = ""
    scan_id: str = ""
    amount: float = 0.0
    status: str = "Pending"  # "Paid" | "Pending"
    payment_date: str = ""
    method: str = "Credit Card"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Payment":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})
