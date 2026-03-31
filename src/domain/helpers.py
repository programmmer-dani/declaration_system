from domain.security.hashing import verify_restore_code
from infrastructure.backup_infrastructure import fetch_all_backups
from infrastructure.database import fetch_all_managers, fetch_all_restore_codes
from presentation.helpers import input_restore_code, print_and_select_from_list
from domain.security.encryption import decrypt_value

def select_manager():
    managers = fetch_all_managers()
    managers_names = [decrypt_value(manager) for manager in managers]
    manager = print_and_select_from_list(managers_names)
    index = managers_names.index(manager)
    return managers[index]

def select_backup():
    backups = fetch_all_backups()
    backup = print_and_select_from_list(backups)
    return backup

def select_restore_code():
    restore_codes = fetch_all_restore_codes()
    inputted_restore_code = input_restore_code()
    matching_restorecode_object = None
    for code in restore_codes:
        if verify_restore_code(inputted_restore_code, code["restore_code_hash"]):
            return matching_restorecode_object
    return None