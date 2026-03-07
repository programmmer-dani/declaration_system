from datetime import UTC, datetime

from security.auth import hash_password, hash_username
from security.encryption import encrypt_value


def secure_user_data(user):
    """user: dict with username, password, first_name, last_name, role. Returns DB-ready dict with encrypted/hashed fields."""
    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S")
    return {
        "role": user["role"],
        "username_enc": encrypt_value(user["username"]),
        "username_lookup": hash_username(user["username"]),
        "password_hash": hash_password(user["password"]),
        "first_name_enc": encrypt_value(user["first_name"]),
        "last_name_enc": encrypt_value(user["last_name"]),
        "registration_date": now,
        "is_active": 1,
    }
