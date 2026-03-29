import secrets
from domain.helpers import select_backup, select_manager
from domain.security.security import hash_backup_restore_code
from infrastructure.backup import fetch_all_backups, overwrite_db
from infrastructure.database import save_assigned_backup
from presentation.helpers import print_and_select_from_list


def restore_any_backup(session=None):
    backups = fetch_all_backups()
    name = print_and_select_from_list(backups, "Choose backup to restore: ")
    if not name:
        return None
    overwrite_db(name)
    return "logout"

def generate_backup_restore_code():
    return secrets.token_urlsafe(16)

def assign_backup():
    restore_code = generate_backup_restore_code()
    restore_code_hash = hash_backup_restore_code(restore_code)
    manager = select_manager()
    backup_name = select_backup() # string of name refering to on disk file, backupfile is not in db, so handle errors correctely
    save_assigned_backup(manager["user_id"], backup_name, restore_code_hash) # check if backupname also needs filepath included