from datetime import UTC, datetime

from security.auth import hash_password, hash_username
from security.encryption import encrypt_value


def secure_user_data(user):
    """Turn raw user (username, password, first_name, last_name, role) into DB-ready dict with encrypted/hashed fields."""
    u = user if isinstance(user, dict) else vars(user)
    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S")
    return {
        "role": u["role"],
        "username_enc": encrypt_value(u["username"]),
        "username_lookup": hash_username(u["username"]),
        "password_hash": hash_password(u["password"]),
        "first_name_enc": encrypt_value(u["first_name"]),
        "last_name_enc": encrypt_value(u["last_name"]),
        "registration_date": now,
        "is_active": 1,
    }
