import secrets
from domain.helpers import select_backup, select_manager, select_restore_code
from domain.security.hashing import hash_restore_code, verify_restore_code
from infrastructure.backup_infrastructure import fetch_all_backups, overwrite_db, set_restore_code_revoked
from infrastructure.database import fetch_restore_code_by_manager_id, save_assigned_backup
from presentation.helpers import display_restorecode_status, input_restore_code, print_and_select_from_list


def restore_any_backup(session):
    backups = fetch_all_backups()
    name = print_and_select_from_list(backups, "Choose backup to restore: ")
    if not name:
        return None
    overwrite_db(name)
    return "logout"

def restore_backup_with_code(session):
    inputted_restore_code = input_restore_code()
    manager_id = session["user_id"]
    restore_code_objects = fetch_restore_code_by_manager_id(manager_id)
    for restore_code_object in restore_code_objects:
        if verify_restore_code(inputted_restore_code, restore_code_object["restore_code_hash"]):
            overwrite_db(restore_code_object["backup_filename"]) # test if needs to be filename or complete path + filename
            return "logout"
    raise Exception("Invalid restore code.")

def generate_backup_restore_code():
    return secrets.token_urlsafe(16)

def assign_backup(session):
    restore_code = generate_backup_restore_code()
    restore_code_hash = hash_restore_code(restore_code)
    manager = select_manager()
    backup_name = select_backup() # string of name refering to on disk file, backupfile is not in db, so handle errors correctely
    save_assigned_backup(manager["user_id"], backup_name, restore_code_hash) # check if backupname also needs filepath included
    
def view_restore_code_status(session):
    restore_code = select_restore_code()
    used = restore_code["is_used"]
    revoked = restore_code["is_revoked"]
    display_restorecode_status(used, revoked)
    
def revoke_restore_code(session):
    verified_restorecode_object = select_restore_code()
    if verified_restorecode_object:
        set_restore_code_revoked(verified_restorecode_object)
    raise Exception("Invalid restore code.")