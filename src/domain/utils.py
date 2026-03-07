from datetime import UTC, datetime

from security.auth import hash_password, hash_username
from security.encryption import decrypt_value, encrypt_value


def secure_user_data(user):
    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S")
    return {
        "role": user["role"],
        "username_enc": encrypt_value(user["username"]),
        "username_lookup": hash_username(user["username"]),
        "password_hash": hash_password(user["password"]),
        "first_name_enc": encrypt_value(user["first_name"]),
        "last_name_enc": encrypt_value(user["last_name"]),
        "registration_date": now,
        "is_active": 1,
    }


def _decrypt_row(row_dict, enc_columns):
    out = dict(row_dict)
    for col in enc_columns:
        if col in out and out[col] is not None:
            out[col] = decrypt_value(out[col])
    return out


def print_db_content():
    #AI generated func, outputting DB data for debugging purposes
    import sqlite3
    from infrastructure.database import get_connection

    tables = [
        ("users", ["username_enc", "first_name_enc", "last_name_enc"]),
        ("employees", [
            "first_name_enc", "last_name_enc", "birthday_enc", "gender_enc",
            "street_name_enc", "house_number_enc", "zip_code_enc", "city_enc",
            "email_enc", "mobile_phone_enc", "id_doc_type_enc", "id_doc_number_enc", "bsn_enc",
        ]),
        ("claims", [
            "project_number_enc", "travel_distance_enc", "from_zip_enc", "from_house_number_enc",
            "to_zip_enc", "to_house_number_enc", "salary_batch_enc",
        ]),
    ]
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        for table_name, enc_cols in tables:
            cur = conn.execute(f"SELECT * FROM {table_name}")
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description]
            enc_cols = [c for c in enc_cols if c in cols]
            print(f"\n=== {table_name.upper()} (as stored) ===")
            for row in rows:
                print(dict(row))
            print(f"\n=== {table_name.upper()} (decrypted) ===")
            for row in rows:
                print(_decrypt_row(dict(row), enc_cols))
