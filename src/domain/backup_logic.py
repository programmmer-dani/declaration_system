import secrets
from domain.helpers import request_managers, select_backup, select_manager, select_restore_code
from domain.security.encryption import decrypt_value, encrypt_value
from domain.security.hashing import hash_restore_code, verify_restore_code
from infrastructure.backup_infrastructure import fetch_all_backups, overwrite_db, set_restore_code_revoked
from infrastructure.database import fetch_restore_code_by_manager_id, save_assigned_backup, set_restore_code_used
from logging_system import log_event
from presentation.helpers import display_restorecode_status, input_restore_code, print_and_select_from_list, print_error


def restore_any_backup(session):
    if session["role"] == "admin":
        backups = fetch_all_backups()
        if not backups:
            print_error("No backups found")
            return None
        name = print_and_select_from_list(backups)
        if not name:
            return None
        overwrite_db(name)
        log_event("backup restored", username_enc=session["username_enc"], additional_info=f"backup restored: {name}")
        print(f"Backup '{name}' restored successfully.")
        return "logout"
    log_event("unauthorized backup restore attempt", username_enc=session["username_enc"], is_suspicious=True)
    raise Exception("Unauthorized access")

def restore_backup_with_code(session):
    
    if session["role"] == "manager":
        restore_code_object = None
        restore_code_found = False
        manager_found = False
        manager_id = session["user_id"]
        managers = request_managers()
        restore_code_list = fetch_restore_code_by_manager_id(manager_id)
        
        inputted_restore_code = input_restore_code()
        
        if not inputted_restore_code or not restore_code_list or len(restore_code_list) < 1:
            print_error("Invalid restore code")
            log_event("Invalid restore code", username_enc=session["username_enc"])
            return
        
        for restore_code in restore_code_list:
            if verify_restore_code(inputted_restore_code, restore_code["code_hash"]):
                restore_code_found = True
                if restore_code["is_used"] == 1:
                    print_error("Invalid restore code")
                    log_event("Invalid restore code", username_enc=session["username_enc"], additional_info=f"Already used restorecode attempt. code: {inputted_restore_code} for manager: {manager_id}")
                    return
                if restore_code["is_revoked"] == 1:
                    print_error("Invalid restore code")
                    log_event("Invalid restore code", username_enc=session["username_enc"], additional_info=f"Revoked restorecode attempt. code: {inputted_restore_code} for manager: {manager_id}")
                    return
                
                try: 
                    overwrite_db(decrypt_value(restore_code["backup_filename_enc"]))
                    restore_code_object = restore_code
                    log_event("backup restored", username_enc=session["username_enc"], additional_info=f"backup restored: {decrypt_value(restore_code_object["backup_filename_enc"])}")
                except Exception as e:
                    print_error(f"Restoring backup failed")
                    log_event("Restoring backup failed", username_enc=session["username_enc"], additional_info=f"Restoring backup failed: {e}")
                    return
            if restore_code_found: break
        
        if not restore_code_found:
            print_error("Invalid restore code")
            log_event("Invalid restore code", username_enc=session["username_enc"], additional_info=f"Invalid restorecode attempt. code: {inputted_restore_code} for manager: {manager_id}")
            return
            
        if managers and len(managers) > 0 and restore_code_object:
            for manager in managers:
                if manager["user_id"] == restore_code_object["manager_user_id"]:
                    manager_found = True
                    codes = fetch_restore_code_by_manager_id(manager["user_id"])
                    managers_codes_found = False
                    if codes and len(codes) > 0:
                        for code in codes:
                            if code["restore_code_id"] == restore_code_object["restore_code_id"]:
                                managers_codes_found = True
                                set_restore_code_used(code["restore_code_id"])
                                log_event("restore code marked as used", username_enc=session["username_enc"], additional_info=f"code id: {restore_code_object["restore_code_id"]}")
                        if managers_codes_found: break
                if manager_found: break
                
        return "logout"
    
    else:
        log_event("unauthorized backup restore code use attempt", username_enc=session["username_enc"], is_suspicious=True)
        raise Exception("Unauthorized access")

def generate_backup_restore_code():
    return secrets.token_urlsafe(16)

def assign_backup(session):
    if session["role"] == "admin":
        restore_code = generate_backup_restore_code()
        restore_code_hash = hash_restore_code(restore_code)
        
        manager = select_manager()
        if not manager:
            return
        
        backup = select_backup()
        if not backup:
            return
        
        backup_name_enc = encrypt_value(backup)
        save_assigned_backup(manager["user_id"], backup_name_enc, restore_code_hash)
        log_event("backup restore code assigned", username_enc=session["username_enc"], additional_info=f"restore code: {restore_code} for manager: {manager["user_id"]} for backup file: {decrypt_value(backup_name_enc)}")
        print(f"\n\nThe restore code is: {restore_code}")
        return
    
    log_event("unauthorized backup restore code assign attempt", username_enc=session["username_enc"], is_suspicious=True)
    raise Exception("Unauthorized access")
    
def view_restore_code_status(session):
    if session["role"] == "admin":
        restore_code = select_restore_code()
        if not restore_code:
            print_error("Invalid restore code")
            log_event("Invalid restore code", username_enc=session["username_enc"])
            return
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
        if not verified_restorecode_object:
            print_error("Invalid restore code")
            log_event("Invalid restore code", username_enc=session["username_enc"])
            return
        if verified_restorecode_object and not None:
            set_restore_code_revoked(verified_restorecode_object)
            print("Restore code revoked successfully.")
            log_event("restore code revoked", username_enc=session["username_enc"], additional_info=f"restore code revoked (id: {verified_restorecode_object["restore_code_id"]})")
            return
        print_error("Invalid restore code.")
        log_event("Invalid restore code", username_enc=session["username_enc"])
        return
    log_event("unauthorized restore code revoke attempt", username_enc=session["username_enc"], is_suspicious=True)
    raise Exception("Unauthorized access")