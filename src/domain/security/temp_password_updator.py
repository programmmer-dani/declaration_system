from domain.security.hashing import hash_password, verify_password
from infrastructure.database import find_user_by_username, save_new_password
from domain.security.encryption import decrypt_value
from domain.security.validation import validate_password
from presentation.helpers import go_validate, print_error


def update_temp_password(user):
    new_password = go_validate("Enter new password: ", validate_password)
    new_password_hash = hash_password(new_password)
    old_password_hash = find_user_by_username(decrypt_value(user["username_enc"]))["password_hash"]
    while verify_password(new_password_hash, old_password_hash):
        print_error("Password cannot be the same as the temporary password")
        new_password = go_validate("Enter new password: ", validate_password)
        new_password_hash = hash_password(new_password)
    save_new_password(user["user_id"], new_password_hash)