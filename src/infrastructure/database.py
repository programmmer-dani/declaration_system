import os
import sqlite3


from domain.security.encryption import decrypt_value, encrypt_value
from domain.security.hashing import hash_username
from infrastructure.config import DATABASE_PATH

def fetch_role_by_username_enc(username_enc):
    if username_enc is None:
        return None
    lookup = hash_username(decrypt_value(username_enc))
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT role_enc FROM users WHERE username_lookup = ?",
            (lookup,),
        )
        row = cur.fetchone()
        return decrypt_value(row["role_enc"]) if row is not None else None

def fetch_all_logs():
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM logs")
        logs = cur.fetchall()
        return logs

def fetch_all_managers():
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM users")
        users = cur.fetchall()
        return [user for user in users if decrypt_value(user["role_enc"]) == "manager"]

def fetch_unread_suspicious_logs():
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM logs WHERE is_read = 0")
        logs = cur.fetchall()
        return [log for log in logs if decrypt_value(log["is_suspicious_enc"]) == "1"]

def flag_all_logs_as_read():
    with get_connection() as conn:
        cur = conn.execute("UPDATE logs SET is_read = 1")
        conn.commit()

def fetch_logs_since_created_at(since_created_at):
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT * FROM logs WHERE created_at >= ? ORDER BY log_id DESC",
            (since_created_at,),
        )
        return cur.fetchall()

def fetch_all_employees():
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM users")
        users = cur.fetchall()
        return [user for user in users if decrypt_value(user["role_enc"]) == "employee"]

def fetch_all_claims():
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM claims")
        claims = cur.fetchall()
        return claims

def fetch_all_restore_codes():
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM restore_codes")
        restore_codes = cur.fetchall()
        return restore_codes

def fetch_restore_code_by_manager_id(manager_id):
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM restore_codes")
        rows = cur.fetchall()
        return [r for r in rows if decrypt_value(r["manager_user_id_enc"]) == str(manager_id)]

def fetch_unrevoked_unused_restore_codes():
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM restore_codes WHERE is_revoked = 0 AND is_used = 0")
        restore_codes = cur.fetchall()
        return restore_codes

def fetch_pending_claims():
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM claims")
        claims = cur.fetchall()
        return [c for c in claims if decrypt_value(c["status_enc"]) == "Pending"]

def fetch_employees_claims(user_id):
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM claims")
        claims = cur.fetchall()
        return [c for c in claims if decrypt_value(c["user_id_enc"]) == str(user_id)]

def fetch_pending_employee_claims(user_id):
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM claims")
        claims = cur.fetchall()
        return [c for c in claims if decrypt_value(c["status_enc"]) == "Pending" and decrypt_value(c["user_id_enc"]) == str(user_id)]

# def fetch_claims_without_salary_batch():
#     with get_connection() as conn:
#         cur = conn.execute("SELECT * FROM claims WHERE salary_batch_enc IS NULL")
#         claims = cur.fetchall()
#         return claims


def fetch_employees_claims_with_travel(user_id):
    with get_connection() as conn:
        cur = conn.execute(
            """
            SELECT c.*,
                   tc.travel_distance_enc,
                   tc.from_zip_enc,
                   tc.from_house_number_enc,
                   tc.to_zip_enc,
                   tc.to_house_number_enc
            FROM claims c
            LEFT JOIN travel_claims tc ON tc.claim_id = c.claim_id
            """
        )
        rows = cur.fetchall()
        return [r for r in rows if decrypt_value(r["user_id_enc"]) == str(user_id)]


def save_approved_claim(claim_id, approved_by_user_id):
    with get_connection() as conn:
        conn.execute(
            "UPDATE claims SET status_enc = ?, approved_by_user_id_enc = ? WHERE claim_id = ?",
            (encrypt_value("Approved"), encrypt_value(str(approved_by_user_id)), claim_id),
        )
        conn.commit()

def save_rejected_claim(claim_id, rejected_by_user_id):
    with get_connection() as conn:
        conn.execute(
            "UPDATE claims SET status_enc = ?, approved_by_user_id_enc = ? WHERE claim_id = ?",
            (encrypt_value("Rejected"), encrypt_value(str(rejected_by_user_id)), claim_id),
        )
        conn.commit()

def save_assigned_backup(manager_user_id, backup_name_enc, restore_code_hash):
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO restore_codes (manager_user_id_enc, backup_filename_enc, code_hash)
               VALUES (?, ?, ?)""",
            (encrypt_value(str(manager_user_id)), backup_name_enc, restore_code_hash),
        )
        conn.commit()

def save_new_password(user_id, hashed_password, is_password_temp=0):
    with get_connection() as conn:
        cur = conn.execute("UPDATE users SET password_hash = ?, is_password_temp_enc = ? WHERE user_id = ?", (hashed_password, encrypt_value(str(is_password_temp)), user_id))
        conn.commit()

def set_restore_code_used(restore_code_id):
    with get_connection() as conn:
        cur = conn.execute("UPDATE restore_codes SET is_used = 1 WHERE restore_code_id = ?", (restore_code_id,))
        conn.commit()


def save_claim_edit(claim_id, key_to_update, updated_value):
    ALLOWED_UPDATE_COLUMNS = {"status_enc", "claim_type_enc", "salary_batch_enc", "project_number_enc", "travel_distance_enc", "from_zip_enc", "from_house_number_enc", "to_zip_enc", "to_house_number_enc", "claim_date_enc"}
    TRAVEL_CLAIM_COLUMNS = {"travel_distance_enc", "from_zip_enc", "from_house_number_enc", "to_zip_enc", "to_house_number_enc"}

    if key_to_update not in ALLOWED_UPDATE_COLUMNS:
        raise ValueError("Corrupted claim data")

    table_to_update = "travel_claims" if key_to_update in TRAVEL_CLAIM_COLUMNS else "claims"
    with get_connection() as conn:
        cur = conn.execute( #if updating claim type (home -> travel) it will update travel table but the claim doesn't exist there
            f"UPDATE {table_to_update} SET {key_to_update} = ? WHERE claim_id = ?",
            (updated_value, claim_id),
        )
        conn.commit()

def save_employee_edit(employee_id, key_to_update, updated_value):
    ALLOWED_UPDATE_COLUMNS = {"first_name_enc", "last_name_enc", 'birthday_enc', 'gender_enc', 'street_name_enc', 'house_number_enc', 'zip_code_enc', 'city_enc', 'email_enc', 'mobile_phone_enc', 'id_doc_type_enc', 'id_doc_number_enc', 'bsn_enc'}
    if key_to_update not in ALLOWED_UPDATE_COLUMNS:
        raise ValueError("Invalid update key")
    with get_connection() as conn:
        conn.execute(f"UPDATE employees SET {key_to_update} = ? WHERE user_id = ?", (updated_value, employee_id))
        if key_to_update in ("first_name_enc", "last_name_enc"):
            conn.execute(f"UPDATE users SET {key_to_update} = ? WHERE user_id = ?", (updated_value, employee_id))
        conn.commit()

def save_manager_edit(manager_id, key_to_update, updated_value):
    ALLOWED_UPDATE_COLUMNS = {"first_name_enc", "last_name_enc"}
    if key_to_update not in ALLOWED_UPDATE_COLUMNS:
        raise ValueError("Invalid update key")
    with get_connection() as conn:
        cur = conn.execute(f"UPDATE users SET {key_to_update} = ? WHERE user_id = ?", (updated_value, manager_id))
        conn.commit()

def delete_employee_from_db(employee_id):
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM users WHERE user_id = ?", (employee_id,))
        conn.commit()

def delete_claim_from_db(claim_id):
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM claims WHERE claim_id = ?", (claim_id,))
        conn.commit()

def save_claim(claim):
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO claims (
                user_id_enc,
                claim_date_enc,
                project_number_enc,
                claim_type_enc,
                status_enc,
                approved_by_user_id_enc,
                salary_batch_enc
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                claim["user_id_enc"],
                claim["claim_date_enc"],
                claim["project_number_enc"],
                claim["claim_type_enc"],
                claim["status_enc"],
                claim.get("approved_by_user_id_enc"),
                claim.get("salary_batch_enc"),
            ),
        )
        claim_id = cur.lastrowid
        if decrypt_value(claim["claim_type_enc"]) == "Travel":
            conn.execute(
                """
                INSERT INTO travel_claims (
                    claim_id,
                    travel_distance_enc,
                    from_zip_enc,
                    from_house_number_enc,
                    to_zip_enc,
                    to_house_number_enc
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    claim_id,
                    claim["travel_distance_enc"],
                    claim["from_zip_enc"],
                    claim["from_house_number_enc"],
                    claim["to_zip_enc"],
                    claim["to_house_number_enc"],
                ),
            )

        conn.commit()


def save_user(registration_date_enc, user, role):
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO users (role_enc, username_enc, username_lookup, password_hash, is_password_temp_enc, first_name_enc, last_name_enc, registration_date_enc)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                user["role_enc"],
                user["username_enc"],
                user["username_lookup"],
                user["password_hash"],
                encrypt_value("0"),
                user["first_name_enc"],
                user["last_name_enc"],
                registration_date_enc,
            ),
        )
        user_id = cur.lastrowid
        if role == "employee":
            conn.execute(
                """INSERT INTO employees (user_id, first_name_enc, last_name_enc, birthday_enc, gender_enc, street_name_enc, house_number_enc, zip_code_enc, city_enc, email_enc, mobile_phone_enc, id_doc_type_enc, id_doc_number_enc, bsn_enc, registration_date_enc)
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
                    registration_date_enc,
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
            "SELECT * FROM users WHERE username_lookup = ?",
            (lookup,),
        )
        return cur.fetchone()

def get_user_id_by_username(username):
    lookup = hash_username(username)
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT user_id FROM users WHERE username_lookup = ?",
            (lookup,),
        )
        row = cur.fetchone()
        return row["user_id"] if row is not None else None


def save_log(ts, username_enc, activity_desc_enc, is_suspicious_enc, additional_info_enc=None):
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO logs (created_at, username_enc, activity_desc_enc, is_suspicious_enc, additional_info_enc) VALUES (?, ?, ?, ?, ?)",
            (ts, username_enc, activity_desc_enc, is_suspicious_enc, additional_info_enc),
        )
        conn.commit()

def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
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
            role_enc BLOB NOT NULL,
            username_enc BLOB NOT NULL,
            username_lookup TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            is_password_temp_enc BLOB NOT NULL,
            first_name_enc BLOB NOT NULL,
            last_name_enc BLOB NOT NULL,
            registration_date_enc BLOB NOT NULL
        );

        CREATE TABLE IF NOT EXISTS employees (
            user_id INTEGER PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
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
            registration_date_enc BLOB NOT NULL
        );

        CREATE TABLE IF NOT EXISTS claims (
            claim_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id_enc BLOB NOT NULL,
            claim_date_enc BLOB NOT NULL,
            project_number_enc BLOB NOT NULL,
            claim_type_enc BLOB NOT NULL,
            status_enc BLOB NOT NULL,
            approved_by_user_id_enc BLOB,
            salary_batch_enc BLOB
        );

        CREATE TABLE IF NOT EXISTS travel_claims (
            claim_id INTEGER PRIMARY KEY REFERENCES claims(claim_id) ON DELETE CASCADE,
            travel_distance_enc BLOB NOT NULL,
            from_zip_enc BLOB NOT NULL,
            from_house_number_enc BLOB NOT NULL,
            to_zip_enc BLOB NOT NULL,
            to_house_number_enc BLOB NOT NULL
        );

        CREATE TABLE IF NOT EXISTS restore_codes (
            restore_code_id INTEGER PRIMARY KEY AUTOINCREMENT,
            manager_user_id_enc BLOB NOT NULL,
            backup_filename_enc BLOB NOT NULL,
            code_hash TEXT NOT NULL UNIQUE,
            is_used INTEGER NOT NULL DEFAULT 0 CHECK (is_used IN (0, 1)),
            is_revoked INTEGER NOT NULL DEFAULT 0 CHECK (is_revoked IN (0, 1))
        );

        CREATE TABLE IF NOT EXISTS logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            username_enc BLOB,
            activity_desc_enc BLOB NOT NULL,
            additional_info_enc BLOB,
            is_suspicious_enc BLOB NOT NULL,
            is_read INTEGER NOT NULL DEFAULT 0 CHECK (is_read IN (0, 1))
        );

        """
    )
    conn.commit()
