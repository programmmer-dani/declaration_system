from domain.backup_logic import list_backups
from infrastructure.backup import fetch_all_backups
from infrastructure.database import fetch_all_managers
from presentation.helpers import print_and_select_from_list
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