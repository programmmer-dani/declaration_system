from infrastructure.backup import fetch_all_backups, overwrite_db
from presentation.helpers import select_backup


def restore_backup(session=None):
    name = select_backup()
    if not name:
        return None
    overwrite_db(name)
    return "logout"
    

def list_backups():
    backuplist = fetch_all_backups()
    return backuplist