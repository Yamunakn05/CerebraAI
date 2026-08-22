# utils/constants.py
# ============================================================
# Shared constants for the Brain Tumor AI Platform
# ============================================================

import os

# ── Paths ──────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

MODEL_PATH = os.path.join(MODELS_DIR, "brain_tumor_model.h5")
BEST_MODEL_PATH = os.path.join(MODELS_DIR, "best_model.h5")

# ── Model ──────────────────────────────────────────────────
IMG_SIZE = 128
CLASSES = ["glioma", "meningioma", "pituitary", "notumor"]
CLASS_LABELS = {
    "glioma": "Glioma",
    "meningioma": "Meningioma",
    "pituitary": "Pituitary Tumor",
    "notumor": "No Tumor Detected",
}

CLASS_INFO = {
    "glioma": {
        "description": "Gliomas are tumors that arise from glial cells in the brain or spine. They are the most common type of primary brain tumor.",
        "common_symptoms": ["Headaches", "Seizures", "Memory problems", "Personality changes", "Vision problems"],
        "icon": "🔴",
        "risk": "high",
    },
    "meningioma": {
        "description": "Meningiomas arise from the meninges — the membranes surrounding the brain and spinal cord. Most are benign and slow-growing.",
        "common_symptoms": ["Headaches", "Vision changes", "Hearing loss", "Memory loss", "Weakness in limbs"],
        "icon": "🟡",
        "risk": "moderate",
    },
    "pituitary": {
        "description": "Pituitary tumors form in the pituitary gland at the base of the brain. Most are non-cancerous adenomas.",
        "common_symptoms": ["Hormonal imbalances", "Vision problems", "Headaches", "Fatigue", "Mood changes"],
        "icon": "🟠",
        "risk": "moderate",
    },
    "notumor": {
        "description": "No tumor patterns were detected in this MRI scan. The scan appears within normal limits.",
        "common_symptoms": [],
        "icon": "🟢",
        "risk": "none",
    },
}

# ── Severity ────────────────────────────────────────────────
SEVERITY_LEVELS = {
    "Mild": {"color": "#22c55e", "emoji": "🟢", "score_range": (0, 25)},
    "Moderate": {"color": "#eab308", "emoji": "🟡", "score_range": (25, 50)},
    "Severe": {"color": "#f97316", "emoji": "🟠", "score_range": (50, 75)},
    "Critical": {"color": "#ef4444", "emoji": "🔴", "score_range": (75, 100)},
}

# ── Brain Regions ───────────────────────────────────────────
BRAIN_REGIONS = {
    "Frontal Lobe": {
        "functions": ["Decision making", "Problem solving", "Motor control", "Emotional regulation", "Speech production"],
        "impact": "Tumor in this region may affect personality, voluntary movement, and executive functions.",
    },
    "Temporal Lobe": {
        "functions": ["Memory formation", "Language comprehension", "Hearing", "Emotion processing"],
        "impact": "Tumor in this region may affect memory, hearing, and language understanding.",
    },
    "Parietal Lobe": {
        "functions": ["Sensory processing", "Spatial awareness", "Reading", "Mathematical reasoning"],
        "impact": "Tumor in this region may affect touch perception, spatial orientation, and reading ability.",
    },
    "Occipital Lobe": {
        "functions": ["Visual processing", "Color perception", "Motion detection"],
        "impact": "Tumor in this region may cause visual disturbances or loss of vision.",
    },
    "Cerebellum": {
        "functions": ["Balance", "Coordination", "Fine motor control", "Posture"],
        "impact": "Tumor in this region may affect balance, coordination, and walking.",
    },
    "Brain Stem": {
        "functions": ["Breathing", "Heart rate", "Blood pressure", "Sleep", "Consciousness"],
        "impact": "Tumor in this region is particularly serious as it controls vital functions.",
    },
}

# ── Treatments ──────────────────────────────────────────────
TREATMENTS = {
    "glioma": [
        {"name": "Surgical Resection", "desc": "Removal of as much tumor tissue as possible."},
        {"name": "Radiation Therapy", "desc": "High-energy rays to kill remaining tumor cells."},
        {"name": "Chemotherapy", "desc": "Temozolomide is commonly used for glioblastoma."},
        {"name": "Targeted Therapy", "desc": "Bevacizumab may be used for recurrent glioma."},
    ],
    "meningioma": [
        {"name": "Active Surveillance", "desc": "Monitoring with periodic MRI for slow-growing tumors."},
        {"name": "Surgical Removal", "desc": "Primary treatment for symptomatic meningiomas."},
        {"name": "Radiation Therapy", "desc": "Stereotactic radiosurgery for inoperable cases."},
    ],
    "pituitary": [
        {"name": "Medical Management", "desc": "Dopamine agonists or somatostatin analogues for hormonal tumors."},
        {"name": "Transsphenoidal Surgery", "desc": "Minimally invasive surgery through the nasal passage."},
        {"name": "Radiation Therapy", "desc": "Used when surgery is not feasible or incomplete."},
    ],
    "notumor": [],
}

# ── Accessibility ───────────────────────────────────────────
SUPPORTED_LANGUAGES = {
    "English": "en",
    "Hindi": "hi",
    "Kannada": "kn",
    "Tamil": "ta",
}

# ── App Config ──────────────────────────────────────────────
APP_NAME = "CerebraAI Diagnostic System"
APP_VERSION = "2.1.0"
MEDICAL_DISCLAIMER = (
    "⚠️ MEDICAL DISCLAIMER: This AI system is designed for educational and "
    "research purposes only. It is NOT a substitute for professional medical "
    "diagnosis, advice, or treatment. Always consult a certified neurologist "
    "or qualified healthcare professional for medical decisions."
)
