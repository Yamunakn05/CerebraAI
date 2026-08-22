# auth/local_auth.py
# ============================================================
# Authentication with bcrypt password hashing
# ============================================================

import bcrypt
from datetime import datetime
from typing import Optional, Tuple, Dict, Any

from database.mongo_db import find_user_by_email, create_user, update_user, find_user_by_username
from database.schema import User


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    salt = bcrypt.gensalt(rounds=10)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify a plaintext password against stored bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def register_user(
    username: str,
    email: str,
    password: str,
    full_name: str,
    role: str = "patient",
    age: Optional[int] = None,
    gender: str = "",
    phone: str = "",
    weight: float = 70.0,
    blood_group: str = "O+",
    allergies: str = "None",
    surgeries: str = "None",
) -> Tuple[bool, str]:
    """
    Register a new user.
    Returns: (success: bool, message: str)
    """
    username = (username or "").strip()
    email = (email or "").strip().lower()
    full_name = (full_name or "").strip()

    # Validation
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if "@" not in email:
        return False, "Please enter a valid email address."
    if find_user_by_email(email):
        return False, "An account with this email already exists."
    if find_user_by_username(username):
        return False, "This username is already taken."

    pw_hash = hash_password(password)
    user = User(
        username=username,
        email=email,
        password_hash=pw_hash,
        full_name=full_name,
        role=role,
        age=age,
        gender=gender,
        phone=phone,
        weight=weight,
        blood_group=blood_group,
        allergies=allergies,
        surgeries=surgeries,
    )
    success = create_user(user)
    if success:
        return True, f"Account created successfully! Welcome, {full_name}."
    return False, "Registration failed. Please try again."


def login_user(email: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Authenticate a user by email or username + password.
    Returns: (success: bool, message: str, user_dict: Optional[dict])
    """
    identifier = (email or "").strip()
    if not identifier:
        return False, "Email address or username is required.", None

    user_dict = find_user_by_email(identifier.lower())
    if not user_dict:
        user_dict = find_user_by_username(identifier)
    if not user_dict:
        user_dict = find_user_by_username(identifier.lower())

    if not user_dict:
        return False, "No account found with this email address or username.", None

    pw_input = password or ""
    hash_str = user_dict.get("password_hash", "")

    if not (verify_password(pw_input, hash_str) or verify_password(pw_input.strip(), hash_str)):
        return False, "Incorrect password. Please try again.", None

    # Update last login
    now_iso = datetime.now().isoformat()
    update_user(user_dict["user_id"], {"last_login": now_iso})
    user_dict["last_login"] = now_iso

    return True, f"Welcome back, {user_dict.get('full_name', user_dict['username'])}!", user_dict


def change_password(user_id: str, old_password: str, new_password: str) -> Tuple[bool, str]:
    """Change user password after verifying old one."""
    from database.mongo_db import find_user_by_id
    user_dict = find_user_by_id(user_id)
    if not user_dict:
        return False, "User not found."
    if not verify_password(old_password, user_dict.get("password_hash", "")):
        return False, "Current password is incorrect."
    if len(new_password) < 6:
        return False, "New password must be at least 6 characters."
    new_hash = hash_password(new_password)
    update_user(user_id, {"password_hash": new_hash})
    return True, "Password changed successfully."


def validate_session(user_dict: Optional[Dict]) -> bool:
    """Check if a user session dict is valid."""
    return (
        user_dict is not None
        and "user_id" in user_dict
        and "email" in user_dict
        and "role" in user_dict
    )
