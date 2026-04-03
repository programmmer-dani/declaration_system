import datetime
from datetime import datetime
from domain.security.hashing import hash_password, verify_restore_code
from domain.security.security import login, secure_claim_data, secure_user_data, verify_existing_username
from domain.security.validation import validate_password
from infrastructure.backup_infrastructure import fetch_all_backups
from infrastructure.database import (
    delete_claim_from_db,
    fetch_all_claims,
    fetch_all_employees,
    fetch_all_managers,
    fetch_all_restore_codes,
    fetch_employees_claims,
    fetch_employees_claims_with_travel,
    fetch_pending_claims,
    save_approved_claim,
    save_claim,
    save_claim_edit,
    save_new_password,
    save_rejected_claim,
    save_user,
)
from presentation.helpers import (
    get_claim_data,
    get_login_input,
    get_user_data,
    go_validate,
    input_claim_search_term,
    input_restore_code,
    print_and_select_from_list,
    print_claim_list,
    print_employee_list,
    print_error,
)
from domain.security.encryption import decrypt_value, encrypt_value


def _normalize_search_text(s):
    return " ".join((s or "").lower().split())


def _claim_row_matches_partial_search(row, needle_normalized):
    parts = [
        str(row["claim_date"] or ""),
        str(row["claim_type"] or ""),
        str(row["status"] or ""),
        decrypt_value(row["project_number_enc"]),
    ]
    if row["claim_type"] == "Travel":
        for key in (
            "travel_distance_enc",
            "from_zip_enc",
            "from_house_number_enc",
            "to_zip_enc",
            "to_house_number_enc",
        ):
            blob = row[key]
            parts.append(decrypt_value(blob) if blob is not None else "")
    haystack = _normalize_search_text(" ".join(parts))
    return needle_normalized in haystack


def search_claims(session):
    if session["role"] == "employee":
        rows = fetch_employees_claims_with_travel(session["user_id"])
        if not rows:
            raise Exception("No claims found")
        needle = _normalize_search_text(input_claim_search_term())
        matched = [r for r in rows if _claim_row_matches_partial_search(r, needle)]
        if not matched:
            print_error("No claims match that search.")
            return
        print_claim_list(matched)
        return
    raise Exception("Unauthorized access")


def update_password(session):
    if session["role"] in ["employee", "manager"]:
        valid_user = login(get_login_input())
        if valid_user is None:
            print_error("Authentication failed, user logged out")
            return "logout"
        password = go_validate("Enter new password: ", validate_password)
        save_new_password(session["user_id"], hash_password(password))
        return
    raise Exception("Unauthorized access")

def delete_claim(session):
    if session["role"] == "employee":
        claims = fetch_employees_claims(session["user_id"])
        if not claims:
            raise Exception("No claims found")
        formatted_claims = format_claim_list(claims)
        claim = print_and_select_from_list(formatted_claims, "Select claim to delete: ")
        claim_id = claim["claim_id"]
        delete_claim_from_db(claim_id)
        return
    raise Exception("Unauthorized access")

def edit_claim(session): # EXTENSIVELY TEST THIS FUNCTION
    if session["role"] == "employee":
        claims = fetch_employees_claims(session["user_id"])
        if not claims:
            raise Exception("No claims found")

        formatted_claims = format_claim_list(claims)
        claim = print_and_select_from_list(formatted_claims, "Select claim to edit: ")
        claim_id = claim["claim_id"]
        keys = get_keys_to_update(claim["claim_type"])
        key_to_update = print_and_select_from_list(keys, "Select key to update: ")
        updated_value = go_validate(f"Enter new value for {key_to_update}: ", find_validator(key_to_update))
        if is_key_value_encrypted(key_to_update):
            updated_value = encrypt_value(updated_value)
            key_to_update = key_to_update + "_enc"
        save_claim_edit(claim_id, key_to_update, updated_value)
        return
    raise Exception("Unauthorized access")

def edit_claim_as_manager(session):
    if session["role"] == "manager":
        claims = fetch_all_claims() # maybe only fetch unaproved claims
        if not claims:
            raise Exception("No claims found")

        formatted_claims = format_claim_list(claims)
        claim = print_and_select_from_list(formatted_claims, "Select claim to edit: ")
        claim_id = claim["claim_id"]
        keys = ["project_number", "travel_distance"]
        key_to_update = print_and_select_from_list(keys, "Select key to update: ")
        updated_value = go_validate(f"Enter new value for {key_to_update}: ", find_validator(key_to_update))
        updated_value = encrypt_value(updated_value)
        key_to_update = key_to_update + "_enc"
        save_claim_edit(claim_id, key_to_update, updated_value)
        return
    raise Exception("Unauthorized access")
    
def find_validator(key_to_update):
    from domain.security.validation import (
        validate_claim_date,
        validate_project_number,
        validate_claim_type,
        validate_travel_distance,
        validate_zip_code,
        validate_house_number,
    )

    validators = {
        "claim_date": validate_claim_date,
        "project_number": validate_project_number,
        "claim_type": validate_claim_type,
        "travel_distance": validate_travel_distance,
        "from_zip_code": validate_zip_code,
        "from_house_number": validate_house_number,
        "to_zip_code": validate_zip_code,
        "to_house_number": validate_house_number,
        "project_number": validate_project_number,
        "travel_distance": validate_travel_distance,
    }

    if key_to_update not in validators:
        raise Exception(f"No validator found for {key_to_update}")
    return validators[key_to_update]
    
def is_key_value_encrypted(key_to_update):
    if key_to_update in ["travel_distance", "from_zip_code", "to_zip_code"]:
        return True
    else:
        return False
    
def get_keys_to_update(claim_type):
    if claim_type == "Travel":
        return [
            "claim_date",
            "project_number",
            "claim_type",
            "travel_distance",
            "from_zip_code",
            "from_house_number",
            "to_zip_code",
            "to_house_number"
        ]
    # For "Home Office", only return general claim keys
    else:
        return [
            "claim_date",
            "project_number",
            "claim_type"
        ]

def approve_claim(session):
    if session["role"] == "manager":
        claims = fetch_pending_claims()
        if not claims:
            raise Exception("No claims found")
        formatted_claims = format_claim_list(claims)
        claim = print_and_select_from_list(formatted_claims, "Select claim to approve: ")
        save_approved_claim(claim["claim_id"], session["user_id"])
        return
    raise Exception("Unauthorized access")
    
def reject_claim(session):
    if session["role"] == "manager":
        claims = fetch_pending_claims()
        if not claims:
            raise Exception("No claims found")
        formatted_claims = format_claim_list(claims)
        claim = print_and_select_from_list(formatted_claims, "Select claim to reject: ")
        save_rejected_claim(claim["claim_id"], session["user_id"])
        return
    raise Exception("Unauthorized access")
    
def format_claim_list(claims): # is this the correct data to display
    return [
        {
            "claim_id": claim["claim_id"],
            "claim_date": claim["claim_date"],
            "claim_type": claim["claim_type"],
            "status": claim["status"],
        }
        for claim in claims
    ]

def create_claim(session):
    if session["role"] == "employee":
        claim_data = get_claim_data()
        secured_claim_data = secure_claim_data(session, claim_data)
        save_claim(secured_claim_data)
        return
    raise Exception("Unauthorized access")

def create_user(session):
    session_role = session["role"]
    if session_role in ["manager", "admin"]:
        if session_role == "admin":
            role = "manager"
        elif session_role == "manager":
            role = "employee"
        else:
            raise Exception("Invalid role to assign to user")
        user_data = get_user_data(role)
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        try:
            verify_existing_username(user_data["username"])
            secured_user_data = secure_user_data(user_data) 
            save_user(now, secured_user_data)
            return
        except ValueError as e:
            raise Exception(e)
    raise Exception("Invalid role")
    # optionally add visual feedback

def select_manager():
    managers = request_managers()
    if not managers:
        raise Exception("No managers found")
    managers_names = [decrypt_value(manager) for manager in managers]
    manager = print_and_select_from_list(managers_names)
    index = managers_names.index(manager)
    return managers[index]

def select_backup():
    backups = fetch_all_backups()
    if not backups:
        raise Exception("No backups found")
    backup = print_and_select_from_list(backups)
    return backup

def select_restore_code():
    restore_codes = fetch_all_restore_codes()
    inputted_restore_code = input_restore_code()
    matching_restorecode_object = None
    for code in restore_codes:
        if verify_restore_code(inputted_restore_code, code["restore_code_hash"]):
            return matching_restorecode_object
    return None

def request_employees_claims(session):
    if session["role"] == "employee":
        claims = fetch_employees_claims(session["user_id"])
        if not claims:
            raise Exception("No claims found")
        print_claim_list(claims)
        return
    raise Exception("Unauthorized access")

def request_managers():
    return fetch_all_managers()

def request_employees():
    return fetch_all_employees()

def request_claims(user_id):
    return fetch_all_claims(user_id)

def format_employee_list(employees):
    return [{"name": f"{decrypt_value(employee['username_enc'])} : {decrypt_value(employee['first_name_enc'])} {decrypt_value(employee['last_name_enc'])}"} for employee in employees]

def view_employee_list(session):
    if session["role"] == "manager":
        employees = request_employees()
        if not employees:
            raise Exception("No employees found")
        employees_list = format_employee_list(employees)    
        print_employee_list(employees_list)
        return
    raise Exception("Unauthorized access")

def view_employees_claims(session):
    if session["role"] == "manager":
        employees = request_employees()
        
        if not employees:
            raise Exception("No employees found")
        
        formatted_employees = format_employee_list(employees)
        employee = print_and_select_from_list(formatted_employees)
        index = formatted_employees.index(employee)
        claims = request_claims(employees[index]["user_id"])
        
        if not claims:
            raise Exception("No claims found")
        
        return print_claim_list(claims, employee["name"])
    raise Exception("Unauthorized access")