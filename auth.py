import json
import os
import hashlib
import secrets
from typing import Dict, Optional


DEFAULT_USERS_FILE = "users.json"


def _get_users_file_path(custom_path: Optional[str] = None) -> str:
    return custom_path or DEFAULT_USERS_FILE


def load_users(file_path: Optional[str] = None) -> Dict[str, Dict[str, str]]:
    path = _get_users_file_path(file_path)
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_users(users: Dict[str, Dict[str, str]], file_path: Optional[str] = None) -> None:
    path = _get_users_file_path(file_path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


def _hash_password(password: str, salt: str) -> str:
    # Use PBKDF2-HMAC with SHA256
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        100_000,
        dklen=32,
    )
    return dk.hex()


def create_user(username: str, password: str, email: Optional[str] = None, file_path: Optional[str] = None) -> bool:
    username = username.strip()
    if not username or not password:
        return False

    users = load_users(file_path)
    if username in users:
        return False

    salt = secrets.token_hex(16)
    password_hash = _hash_password(password, salt)

    users[username] = {
        "salt": salt,
        "password_hash": password_hash,
        "email": (email or "").strip(),
        "verified": False,
        "verify_token": secrets.token_hex(3),  # 6 hex chars (~24 bits)
    }
    save_users(users, file_path)
    return True


def verify_user(username: str, password: str, file_path: Optional[str] = None) -> bool:
    users = load_users(file_path)
    record = users.get(username)
    if not record:
        return False
    expected_hash = record.get("password_hash", "")
    salt = record.get("salt", "")
    if not expected_hash or not salt:
        return False
    given_hash = _hash_password(password, salt)
    # constant-time compare
    if not secrets.compare_digest(given_hash, expected_hash):
        return False
    # require email verification if email present
    if record.get("email"):
        return bool(record.get("verified", False))
    return True


def get_verify_token(username: str, file_path: Optional[str] = None) -> Optional[str]:
    users = load_users(file_path)
    rec = users.get(username)
    if not rec:
        return None
    return rec.get("verify_token")


def set_verified(username: str, file_path: Optional[str] = None) -> bool:
    users = load_users(file_path)
    if username not in users:
        return False
    users[username]["verified"] = True
    users[username]["verify_token"] = ""
    save_users(users, file_path)
    return True


def regenerate_verify_token(username: str, file_path: Optional[str] = None) -> Optional[str]:
    users = load_users(file_path)
    if username not in users:
        return None
    token = secrets.token_hex(3)
    users[username]["verify_token"] = token
    save_users(users, file_path)
    return token


