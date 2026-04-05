import secrets
from domain.helpers import request_managers, select_backup, select_manager, select_restore_code
from domain.security.hashing import hash_restore_code, verify_restore_code
from infrastructure.backup_infrastructure import fetch_all_backups, overwrite_db, set_restore_code_revoked
from infrastructure.database import fetch_restore_code_by_manager_id, save_assigned_backup, set_restore_code_used
from logging_system import log_event
from presentation.helpers import display_restorecode_status, input_restore_code, print_and_select_from_list


def restore_any_backup(session):
    if session["role"] == "admin":
        backups = fetch_all_backups()
        name = print_and_select_from_list(backups)
        if not name:
            return None
        overwrite_db(name)
        log_event("backup restored", username_enc=session["username_enc"], additional_info=f"backup restored: {name}")
        return "logout"
    log_event("unauthorized backup restore attempt", username_enc=session["username_enc"], is_suspicious=True)
    raise Exception("Unauthorized access")

def restore_backup_with_code(session):
    if session["role"] == "manager":
        inputted_restore_code = input_restore_code()
        manager_id = session["user_id"]
        restore_code_object = fetch_restore_code_by_manager_id(manager_id)
        if restore_code_object is None or len(restore_code_object) < 1:
            raise Exception("No restore codes found.")
        if verify_restore_code(inputted_restore_code, restore_code_object["code_hash"]):
            if restore_code_object["is_used"] == 1:
                return Exception("Restore code already used.")
            if restore_code_object["is_revoked"] == 1:
                return Exception("Restore code revoked.")
            try: 
                overwrite_db(restore_code_object["backup_filename"])
                log_event("backup restored", username_enc=session["username_enc"], additional_info=f"backup restored: {restore_code_object["backup_filename"]}")
            except Exception:
                return Exception("Failed to restore backup.")
            managers = request_managers()
            for manager in managers:
                if manager["user_id"] == restore_code_object["manager_user_id"]:
                    codes = fetch_restore_code_by_manager_id(manager["user_id"])
                    for code in codes:
                        if code["id"] == restore_code_object["id"]:
                            set_restore_code_used(code["id"])
                            log_event("backup restore code used", username_enc=session["username_enc"], additional_info=f"code id: {restore_code_object["id"]}")
                return "logout"
            return Exception("Invalid restore code.")
        raise Exception("Invalid restore code.")
    log_event("unauthorized backup restore code use attempt", username_enc=session["username_enc"], is_suspicious=True)
    raise Exception("Unauthorized access")

def generate_backup_restore_code():
    return secrets.token_urlsafe(16)

def assign_backup(session):
    if session["role"] == "admin":
        restore_code = generate_backup_restore_code()
        restore_code_hash = hash_restore_code(restore_code)
        manager = select_manager()
        backup_name = select_backup()
        save_assigned_backup(manager["user_id"], backup_name, restore_code_hash)
        log_event("backup restore code assigned", username_enc=session["username_enc"], additional_info=f"restore code: {restore_code} for manager: {manager["user_id"]}")
        print(f"\n\nThe restore code is: {restore_code}")
        return
    log_event("unauthorized backup restore code assign attempt", username_enc=session["username_enc"], is_suspicious=True)
    raise Exception("Unauthorized access")
    
def view_restore_code_status(session):
    if session["role"] == "admin":
        restore_code = select_restore_code()
        used = restore_code["is_used"]
        revoked = restore_code["is_revoked"]
        display_restorecode_status(used, revoked)
        log_event("restore codes statusus viewed", username_enc=session["username_enc"],)
        return
    log_event("unauthorized restore codes status view attempt", username_enc=session["username_enc"], is_suspicious=True)
    raise Exception("Unauthorized access")
    
def revoke_restore_code(session):
    if session["role"] == "admin":
        verified_restorecode_object = select_restore_code()
        if verified_restorecode_object:
            set_restore_code_revoked(verified_restorecode_object)
            log_event("restore code revoked", username_enc=session["username_enc"], additional_info=f"restore code revoked (id: {verified_restorecode_object["id"]})")
            return
        raise Exception("Invalid restore code.")
    log_event("unauthorized restore code revoke attempt", username_enc=session["username_enc"], is_suspicious=True)
    raise Exception("Unauthorized access")