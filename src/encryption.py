import os
from cryptography.fernet import Fernet

KEY_PATH = "data/master.key"


def load_or_create_key():
    if not os.path.exists(KEY_PATH):
        os.makedirs(os.path.dirname(KEY_PATH), exist_ok=True)
        key = Fernet.generate_key()
        with open(KEY_PATH, "wb") as f:
            f.write(key)
    else:
        with open(KEY_PATH, "rb") as f:
            key = f.read()
    return key


_fernet = Fernet(load_or_create_key())


def encrypt_value(value):
    return _fernet.encrypt(value.encode())


def decrypt_value(value):
    return _fernet.decrypt(value).decode()
