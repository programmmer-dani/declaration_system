import os
import zipfile
from datetime import datetime

from infrastructure.config import BACKUPS_DIR, DATABASE_PATH

def create_backup():
    os.makedirs(BACKUPS_DIR, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S") # what if 2 backups are created simultaniously
    zip_name = f"database_backup_{stamp}.zip"
    zip_path = os.path.join(BACKUPS_DIR, zip_name)

    arcname = os.path.basename(DATABASE_PATH)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(DATABASE_PATH, arcname=arcname)
        
    return zip_path

def fetch_all_backups():
    if not os.path.exists(BACKUPS_DIR):
        return None
    return os.listdir(BACKUPS_DIR)

def overwrite_db(db):
    backup_zip_path = os.path.join(BACKUPS_DIR, db)

    if not os.path.exists(backup_zip_path):
        raise FileNotFoundError(f"Backup file '{db}' does not exist in '{BACKUPS_DIR}'")

    arcname = os.path.basename(DATABASE_PATH)
    with zipfile.ZipFile(backup_zip_path, "r") as zip_ref:
        zip_ref.extract(arcname, BACKUPS_DIR)
    temp_extract_path = os.path.join(BACKUPS_DIR, arcname)

    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)
    os.rename(temp_extract_path, DATABASE_PATH)