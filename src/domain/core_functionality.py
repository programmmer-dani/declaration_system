from turtle import back
from domain.security.security import login
from infrastructure import backup
from infrastructure.backup import fetch_all_backups, overwrite_db
from presentation.helpers import get_login_input, select_backup


def restore_backup():
    name = select_backup()
    if name:
        overwrite_db(name)
    else: 
        raise Exception("No backup to restore selected") 
    # How to forcefully og out?
    # session = login(get_login_input)
    

def list_backups():
    backuplist = fetch_all_backups()
    return backuplist