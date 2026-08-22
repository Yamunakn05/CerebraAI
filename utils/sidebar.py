# utils/sidebar.py
# ============================================================
# Sidebar & Navigation Configuration Helpers for CerebraAI
# ============================================================

from typing import List, Dict, Any
from utils.constants import APP_NAME, APP_VERSION, MEDICAL_DISCLAIMER


def get_navigation_items(role: str = "patient") -> List[Dict[str, str]]:
    """Return navigation links based on user role."""
    base_items = [
        {"name": "Dashboard", "icon": "layout-dashboard", "route": "#dashboard"},
        {"name": "MRI Analysis", "icon": "microscope", "route": "#analysis"},
        {"name": "Medical Records", "icon": "file-text", "route": "#records"},
        {"name": "Appointments", "icon": "calendar", "route": "#appointments"},
        {"name": "Prescriptions", "icon": "pill", "route": "#prescriptions"},
        {"name": "AI Assistant", "icon": "bot", "route": "#chatbot"},
        {"name": "Medicine Store", "icon": "shopping-bag", "route": "#medicine"},
        {"name": "Emergency", "icon": "alert-triangle", "route": "#emergency"},
    ]
    if role in ["admin", "doctor"]:
        base_items.append({"name": "Audit Logs", "icon": "shield-check", "route": "#audit"})
    return base_items


def get_sidebar_brand_info() -> Dict[str, str]:
    """Return branding details for sidebar UI."""
    return {
        "title": APP_NAME,
        "version": APP_VERSION,
        "disclaimer": MEDICAL_DISCLAIMER,
    }
