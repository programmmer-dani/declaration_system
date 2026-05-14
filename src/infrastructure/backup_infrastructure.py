import os
import sqlite3
import zipfile
from datetime import datetime

from infrastructure.config import BACKUPS_DIR, DATABASE_PATH
from infrastructure.database import get_connection


def _merge_newer_logs_from_current_into_restored(restored_db_path, current_db_path):
    if not os.path.exists(current_db_path):
        raise FileNotFoundError(f"Current database file '{current_db_path}' does not exist")
    restored_db_path = os.path.abspath(restored_db_path)
    current_db_path = os.path.abspath(current_db_path)
    conn = sqlite3.connect(restored_db_path)
    try:
        conn.execute("PRAGMA foreign_keys = OFF")
        conn.execute("ATTACH DATABASE ? AS curr", (current_db_path,))
        conn.execute(
            """
            INSERT INTO logs (created_at, username_enc, activity_desc_enc, additional_info_enc, is_suspicious, is_read)
            SELECT c.created_at, c.username_enc, c.activity_desc_enc, c.additional_info_enc, c.is_suspicious, c.is_read
            FROM curr.logs AS c
            WHERE (SELECT MAX(created_at) FROM logs) IS NULL
               OR c.created_at > (SELECT MAX(created_at) FROM logs)
            """
        )
        conn.commit()
    finally:
        try:
            conn.execute("DETACH DATABASE curr")
        except sqlite3.OperationalError:
            raise sqlite3.OperationalError(f"Failed to detach current database from restored database '{restored_db_path}'")
        conn.close()

def create_backup():
    os.makedirs(BACKUPS_DIR, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"database_backup_{stamp}.zip"
    zip_path = os.path.join(BACKUPS_DIR, zip_name)

    arcname = os.path.basename(DATABASE_PATH)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(DATABASE_PATH, arcname=arcname)
        
    return zip_name

def fetch_all_backups():
    if not os.path.exists(BACKUPS_DIR):
        return None
    return os.listdir(BACKUPS_DIR)

def overwrite_db(db):
    backup_zip_path = os.path.join(BACKUPS_DIR, db)

    if not os.path.exists(backup_zip_path):
        raise FileNotFoundError(f"Backup file '{db}' does not exist")

    arcname = os.path.basename(DATABASE_PATH)
    with zipfile.ZipFile(backup_zip_path, "r") as zip_ref:
        zip_ref.extract(arcname, BACKUPS_DIR)
    temp_extract_path = os.path.join(BACKUPS_DIR, arcname)

    if os.path.exists(DATABASE_PATH):
        _merge_newer_logs_from_current_into_restored(temp_extract_path, DATABASE_PATH)
        os.remove(DATABASE_PATH)
    os.rename(temp_extract_path, DATABASE_PATH)
    
def set_restore_code_revoked(restore_code_object):
    with get_connection() as conn:
        cur = conn.execute("UPDATE restore_codes SET is_revoked = 1 WHERE restore_code_id = ?", (restore_code_object["restore_code_id"],))
        conn.commit()