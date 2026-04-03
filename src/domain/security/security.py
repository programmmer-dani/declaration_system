from infrastructure.database import find_user_by_username, username_exists
from domain.security.encryption import decrypt_value, encrypt_value
from domain.security.hashing import hash_password, hash_username, verify_password


def secure_claim_data(session, claim_data):
    secured_claim = {
        "user_id": session["user_id"],
        "claim_date": claim_data["claim_date"],
        "project_number_enc": encrypt_value(claim_data["project_number"]),
        "claim_type": claim_data["claim_type"],
        "status": "Pending",
        "approved_by_user_id": None,
        "salary_batch_enc": None,
    }

    if claim_data["claim_type"] == "Travel":
        secured_claim.update({
            "travel_distance_enc": encrypt_value(claim_data["travel_distance"]),
            "from_zip_enc": encrypt_value(claim_data["from_zip_code"]),
            "from_house_number_enc": encrypt_value(claim_data["from_house_number"]),
            "to_zip_enc": encrypt_value(claim_data["to_zip_code"]),
            "to_house_number_enc": encrypt_value(claim_data["to_house_number"]),
        })

    return secured_claim

def secure_user_data(user_data):
    try:
        secured_user_data = {
            "role": user_data["role"],
            "username_enc": encrypt_value(user_data["username"]),
            "username_lookup": hash_username(user_data["username"]),
            "password_hash": hash_password(user_data["password"]),
            "first_name_enc": encrypt_value(user_data["first_name"]),
            "last_name_enc": encrypt_value(user_data["last_name"]),
            "is_active": 1,
        }
    except ValueError as e:
        raise ValueError(f"Error securing basic user data: {e}")
    try:
        if user_data["role"] == "employee":
            secured_user_data.update(secure_employee_data(user_data))
    except ValueError as e:
        raise ValueError(f"Error securing extra employee data: {e}")
    return secured_user_data
    
    
def secure_employee_data(employee_data):
    return {
        "birthday_enc": encrypt_value(employee_data["birthday"]),
        "gender_enc": encrypt_value(employee_data["gender"]),
        "street_name_enc": encrypt_value(employee_data["street_name"]),
        "house_number_enc": encrypt_value(employee_data["house_number"]),
        "zip_code_enc": encrypt_value(employee_data["zip_code"]),
        "city_enc": encrypt_value(employee_data["city"]),
        "email_enc": encrypt_value(employee_data["email"]),
        "mobile_phone_enc": encrypt_value(employee_data["mobile_phone"]),
        "id_doc_type_enc": encrypt_value(employee_data["id_doc_type"]),
        "id_doc_number_enc": encrypt_value(employee_data["id_doc_number"]),
        "bsn_enc": encrypt_value(employee_data["bsn"]),
    }


def _decrypt_row(row_dict, enc_columns):
    #AI generated func, outputting DB data for debugging purposes
    out = dict(row_dict)
    for col in enc_columns:
        if col in out and out[col] is not None:
            out[col] = decrypt_value(out[col])
    return out


def print_db_content():
    #AI generated func, outputting DB data for debugging purposes
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

def verify_existing_username(username): 
    # Is this func really necessary?
    if username_exists(username):
        raise ValueError("Username already exists")
    
def login(credentials):
    print_db_content() # DONT FORGET TO REMOVE
    if credentials["username"] == "super_admin" and credentials["password"] == "Admin_123?":
        return {"role":"admin"} # ASSIGNMENT REQUIREMENT HARDCODED EXCEPTION
    user = find_user_by_username(credentials["username"])
    if user is None:
        return None
    if verify_password(credentials["password"], user["password_hash"]):
        return user
    return None