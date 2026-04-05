import bcrypt
import hashlib

def hash_username(username):
    normalized = username.strip().lower()
    return hashlib.sha256(normalized.encode()).hexdigest()

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password, stored_hash):
    return bcrypt.checkpw(password.encode(), stored_hash.encode())

def hash_restore_code(code):
    return hashlib.sha256(code.encode()).hexdigest()

def verify_restore_code(code, stored_hash):
    return hash_restore_code(code) == stored_hash
