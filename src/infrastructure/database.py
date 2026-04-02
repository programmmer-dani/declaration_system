import os
import sqlite3


from domain.security.hashing import hash_username
from infrastructure.config import DATABASE_PATH


def fetch_all_managers():
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM users WHERE role = 'manager'")
        managers = cur.fetchall()
        return managers


def fetch_all_employees():
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM users WHERE role = 'employee'")
        employees = cur.fetchall()
        return employees

def fetch_all_claims(employee_id):
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM claims WHERE employee_id = ?", (employee_id,))
        claims = cur.fetchall()
        return claims

def fetch_all_restore_codes():
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM restore_codes")
        restore_codes = cur.fetchall()
        return restore_codes
    
def fetch_restore_code_by_manager_id(manager_id):
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM restore_codes WHERE manager_user_id = ?", (manager_id,))
        restore_code = cur.fetchone()
        return restore_code
    
def fetch_unrevoked_unused_restore_codes():
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM restore_codes WHERE is_revoked = 0 AND is_used = 0")
        restore_codes = cur.fetchall()
        return restore_codes

def save_assigned_backup(manager_user_id, backup_name, restore_code_hash):
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO restore_codes (manager_user_id, backup_filename, code_hash)
               VALUES (?, ?, ?)""",
            (manager_user_id, backup_name, restore_code_hash),
        )
        conn.commit()


def set_restore_code_used(restore_code_id):
    with get_connection() as conn:
        cur = conn.execute("UPDATE restore_codes SET is_used = 1 WHERE restore_code_id = ?", (restore_code_id,))
        conn.commit()


def save_user(registration_date, user,):
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO users (role, username_enc, username_lookup, password_hash, first_name_enc, last_name_enc, registration_date, is_active)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                user["role"],
                user["username_enc"],
                user["username_lookup"],
                user["password_hash"],
                user["first_name_enc"],
                user["last_name_enc"],
                registration_date,
                user.get("is_active", 1),
            ),
        )
        user_id = cur.lastrowid
        if user["role"] == "employee":
            conn.execute(
                """INSERT INTO employees (user_id, first_name_enc, last_name_enc, birthday_enc, gender_enc, street_name_enc, house_number_enc, zip_code_enc, city_enc, email_enc, mobile_phone_enc, id_doc_type_enc, id_doc_number_enc, bsn_enc, registration_date)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    user_id,
                    user["first_name_enc"],
                    user["last_name_enc"],
                    user["birthday_enc"],
                    user["gender_enc"],
                    user["street_name_enc"],
                    user["house_number_enc"],
                    user["zip_code_enc"],
                    user["city_enc"],
                    user["email_enc"],
                    user["mobile_phone_enc"],
                    user["id_doc_type_enc"],
                    user["id_doc_number_enc"],
                    user["bsn_enc"],
                    registration_date,
                ),
            )
        conn.commit()

def username_exists(username):
    lookup = hash_username(username)
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT 1 FROM users WHERE username_lookup = ? LIMIT 1",
            (lookup,),
        )
        return cur.fetchone() is not None


def find_user_by_username(username):
    lookup = hash_username(username)
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT * FROM users WHERE username_lookup = ? AND is_active = 1",
            (lookup,),
        )
        return cur.fetchone()

def get_connection():
    # always call with: with get_connection() as conn:
    # this will close the connection after usage
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    with get_connection() as conn:
        create_tables(conn)


def create_tables(conn: sqlite3.Connection):
    # is_active value is not specefically required for users
    # optional: start using GUIDs
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
            is_revoked INTEGER NOT NULL DEFAULT 0 CHECK (is_revoked IN (0, 1))
        );

        CREATE INDEX IF NOT EXISTS idx_claims_employee_id ON claims(employee_id);
        CREATE INDEX IF NOT EXISTS idx_claims_status ON claims(status);
        """
    )
    conn.commit()