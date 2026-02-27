import os
import sqlite3

from config import DATABASE_PATH


def get_connection():
    # always call with: with get_connection() as conn:
    # this will close the connection after usage
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    with get_connection() as conn:
        create_tables(conn)


def create_tables(conn: sqlite3.Connection):
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL CHECK (role IN ('manager', 'employee')),
            username_enc BLOB NOT NULL,
            username_lookup TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            first_name_enc BLOB NOT NULL,
            last_name_enc BLOB NOT NULL,
            registration_date TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1))
        );

        CREATE TABLE IF NOT EXISTS employees (
            employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE REFERENCES users(user_id) ON DELETE CASCADE,
            first_name_enc BLOB NOT NULL,
            last_name_enc BLOB NOT NULL,
            birthday_enc BLOB NOT NULL,
            gender_enc BLOB NOT NULL,
            street_name_enc BLOB NOT NULL,
            house_number_enc BLOB NOT NULL,
            zip_code_enc BLOB NOT NULL,
            city_enc BLOB NOT NULL,
            email_enc BLOB NOT NULL,
            mobile_phone_enc BLOB NOT NULL,
            id_doc_type_enc BLOB NOT NULL,
            id_doc_number_enc BLOB NOT NULL,
            bsn_enc BLOB NOT NULL,
            registration_date TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS claims (
            claim_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
            claim_date TEXT NOT NULL CHECK (length(claim_date)=10 AND substr(claim_date,5,1)='-' AND substr(claim_date,8,1)='-'),
            project_number_enc BLOB NOT NULL,
            claim_type TEXT NOT NULL CHECK (claim_type IN ('Travel', 'Home Office')),
            travel_distance_enc BLOB,
            from_zip_enc BLOB,
            from_house_number_enc BLOB,
            to_zip_enc BLOB,
            to_house_number_enc BLOB,
            status TEXT NOT NULL DEFAULT 'Pending' CHECK (status IN ('Pending', 'Approved', 'Rejected')),
            approved_by_user_id INTEGER REFERENCES users(user_id),
            salary_batch_enc BLOB,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS restore_codes (
            restore_code_id INTEGER PRIMARY KEY AUTOINCREMENT,
            manager_user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            backup_filename TEXT NOT NULL,
            code_hash TEXT NOT NULL UNIQUE,
            is_used INTEGER NOT NULL DEFAULT 0 CHECK (is_used IN (0, 1)),
            is_revoked INTEGER NOT NULL DEFAULT 0 CHECK (is_revoked IN (0, 1)),
            created_at TEXT NOT NULL,
            used_at TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_claims_employee_id ON claims(employee_id);
        CREATE INDEX IF NOT EXISTS idx_claims_status ON claims(status);
        """
    )
    conn.commit()