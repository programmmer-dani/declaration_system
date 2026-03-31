import bcrypt
import hashlib

def hash_username(username):
    # This function exists to hash usernames (without salt) so they're still determanistic but not revertable to text (in order to lookup usernames in DB)
    normalized = username.strip().lower()
    return hashlib.sha256(normalized.encode()).hexdigest()


def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password, stored_hash):
    return bcrypt.checkpw(password.encode(), stored_hash.encode())

def hash_restore_code(code):
    return hashlib.sha256(code.encode()).hexdigest()

def verify_restore_code(code, stored_hash): # now its deterministic (brute forcing is hard since its already a random code)
    return hash_restore_code(code) == stored_hash
