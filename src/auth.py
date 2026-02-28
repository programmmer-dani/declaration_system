import hashlib
import secrets


def hash_password(password):
    salt = secrets.token_hex()
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
    return f"{salt}:{key.hex()}"


def verify_password(password, stored_hash):
    salt, hex_hash = stored_hash.split(":")
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
    return secrets.compare_digest(key.hex(), hex_hash)
