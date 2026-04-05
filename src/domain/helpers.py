import datetime
import random
import string
from datetime import datetime
from domain.security.hashing import hash_password, verify_restore_code
from domain.security.security import secure_claim_data, secure_user_data, verify_existing_username
from domain.security.validation import validate_password, validate_salary_batch
from infrastructure.backup_infrastructure import fetch_all_backups
from infrastructure.database import (
    delete_claim_from_db,
    delete_employee_from_db,
    fetch_all_claims,
    fetch_all_employees,
    fetch_all_logs,
    fetch_all_managers,
    fetch_all_restore_codes,
    fetch_employees_claims,
    fetch_employees_claims_with_travel,
    fetch_pending_claims,
    flag_all_logs_as_read,
    save_approved_claim,
    save_claim,
    save_claim_edit,
    save_employee_edit,
    save_new_password,
    save_rejected_claim,
    save_user,
)
from logging_system import log_event
from presentation.helpers import (
    get_claim_data,
    get_login_input,
    get_user_data,
    go_validate,
    input_claim_search_term,
    input_employee_search_term,
    input_restore_code,
    print_and_select_from_list,
    print_claim_list,
    print_error,
    print_log_list,
    print_temp_password,
    print_user_list,
)
from domain.security.encryption import decrypt_value, encrypt_value


def _normalize_search_text(s):
    return " ".join((s or "").lower().split())

def _employee_row_matches_partial_search(row, needle_normalized):
    parts = [
        str(decrypt_value(row["username_enc"]) or ""),
        str(decrypt_value(row["first_name_enc"]) or ""),
        str(decrypt_value(row["last_name_enc"]) or ""),
    ]
    haystack = _normalize_search_text(" ".join(parts))
    return needle_normalized in haystack

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

def reset_users_password(session):
    if session["role"] in ["manager", "admin"]:
        if session["role"] == "admin":
            users = [*fetch_all_employees(), *fetch_all_managers()]
        else:
            users = fetch_all_employees()
        if not users:
            raise Exception("No users found")
        formatted_users = format_user_list(users)
        user = print_and_select_from_list(formatted_users, "Select user to reset password: ")
        user_id = user["user_id"]
        temp_password = generate_temp_password()
        temp_password_hash = hash_password(temp_password)
        save_new_password(user_id, temp_password_hash, is_password_temp=1)
        print_temp_password(temp_password)
        log_event("users password reset", username_enc=session["username_enc"], additional_info=f"user: {decrypt_value(user["username_enc"])}")
        return
    log_event("unauthorized users password reset attempt", username_enc=session["username_enc"], is_suspicious=True)
    raise Exception("Unauthorized access")


def generate_temp_password():
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    specials = "~!@#$%&_-+=`|\\()[]{}:;'<>,.?/"
    allowed = lowercase + uppercase + digits + specials

    password = [
        random.choice(lowercase),
        random.choice(uppercase),
        random.choice(digits),
        random.choice(specials),
    ]
    length = random.randint(12, 20)
    password += [random.choice(allowed) for _ in range(length - 4)]
    random.shuffle(password)
    password = ''.join(password)
    if  validate_password(password):
        return password
    return generate_temp_password()

def view_logs(session):
    if session["role"] in ["manager", "admin"]:
        logs = fetch_all_logs()
        if not logs:
            raise Exception("No logs found")
        print_log_list(logs)
        flag_all_logs_as_read()
        log_event("logs viewed", username_enc=session["username_enc"])
        return
    log_event("unauthorized logs view attempt", username_enc=session["username_enc"], is_suspicious=True)
    raise Exception("Unauthorized access")

def edit_employee_account(session):
    if session["role"] == "manager":
        employees = fetch_all_employees()
        if not employees:
            raise Exception("No employees found")
        formatted_employees = format_user_list(employees)
        employee = print_and_select_from_list(formatted_employees, "Select employee to edit: ")
        employee_id = employee["user_id"]
        keys = ["first_name", "last_name", "email", "mobile_phone", "birthday", "bsn", "street_name", "house_number", "zip_code", "city"]
        key_to_update = print_and_select_from_list(keys, "Select key to update: ")
        updated_value = go_validate(f"Enter new value for {key_to_update}: ", find_validator(key_to_update))
        if is_key_value_encrypted(key_to_update):
            updated_value = encrypt_value(updated_value)
            key_to_update = key_to_update + "_enc"
        save_employee_edit(employee_id, key_to_update, updated_value)
        log_event("employee account edited", username_enc=session["username_enc"], additional_info=f"employee account edited (username: {decrypt_value(employee["username_enc"])}: {key_to_update} updated to {updated_value}")
        return
    log_event("unauthorized employee account edit attempt", username_enc=session["username_enc"], is_suspicious=True)
    raise Exception("Unauthorized access")

def set_claims_salary_batch(session, claim_id):
    if session["role"] in ["manager", "admin"]:
        salary_batch = go_validate("Enter salary-batch (YYYY-MM): ", validate_salary_batch)
        save_claim_edit(claim_id, "salary_batch_enc",  encrypt_value(salary_batch))
        return
    raise Exception("Unauthorized access")

def search_claims(session):
    if session["role"] in ["employee", "manager", "admin"]:
        if session["role"] == "employee":
            rows = fetch_employees_claims_with_travel(session["user_id"])
        elif session["role"] == "manager":
            rows = fetch_all_claims()
            if not rows:
                raise Exception("No claims found")
            needle = _normalize_search_text(input_claim_search_term())
            log_event("claims searched", username_enc=session["username_enc"], additional_info=f"claims searched for {needle}")
            matched = [r for r in rows if _claim_row_matches_partial_search(r, needle)]
            if not matched:
                print_error("No claims match that search.")
                return
            print_claim_list(matched)
            return
        else:
            log_event("invalid role claim search attempt", username_enc=session["username_enc"], is_suspicious=True)
            raise Exception("Invalid role")
    log_event("claims searched", username_enc=session["username_enc"], additional_info=f"claims searched for {needle}")
    raise Exception("Unauthorized access")

def search_employees(session):
    if session["role"] in ["manager", "admin"]:
        employees = fetch_all_employees()
        if not employees:
            raise Exception("No employees found")
        needle = _normalize_search_text(input_employee_search_term())
        matched = [r for r in employees if _employee_row_matches_partial_search(r, needle)]
        log_event("employees searched", username_enc=session["username_enc"], additional_info=f"employees searched for {needle}")
        if not matched:
            print_error("No employees match that search.")
            return
        print_user_list(format_user_list(matched))
        return
    log_event("unauthorized employee search attempt", username_enc=session["username_enc"], is_suspicious=True)
    raise Exception("Unauthorized access")


def update_password(session):
    from domain.security.security import login
    
    if session["role"] in ["employee", "manager"]:
        valid_user = login(get_login_input())
        if valid_user is None:
            print_error("Authentication failed, user logged out")
            return "logout"
        password = go_validate("Enter new password: ", validate_password)
        save_new_password(session["user_id"], hash_password(password))
        log_event("password updated", username_enc=session["username_enc"], additional_info=f"password updated for user: {decrypt_value(session["username_enc"])}")
        return
    log_event("unauthorized password update attempt", username_enc=session["username_enc"], is_suspicious=True)
    raise Exception("Unauthorized access")

def edit_manager_account_as_admin(session):
    if session["role"] == "admin":
        managers = fetch_all_managers()
        if not managers:
            raise Exception("No managers found")
        formatted = format_user_list(managers)
        manager = print_and_select_from_list(formatted, "Select manager to edit: ")
        manager_id = manager["user_id"]
        keys = ["first_name", "last_name"]
        key_to_update = print_and_select_from_list(keys, "Select key to update: ")
        updated_value = go_validate(f"Enter new value for {key_to_update}: ", find_validator(key_to_update))
        updated_value = encrypt_value(updated_value)
        key_to_update = key_to_update + "_enc"
        save_employee_edit(manager_id, key_to_update, updated_value)
        log_event("manager account edited", username_enc=session["username_enc"], additional_info=f"manager account edited (id: {manager_id}): {key_to_update} updated to {updated_value}")
        return
    log_event("unauthorized manager account edit attempt", username_enc=session["username_enc"], is_suspicious=True)
    raise Exception("Unauthorized access")

def delete_manager_account_as_admin(session):
    if session["role"] == "admin":
        managers = fetch_all_managers()
        if not managers:
            raise Exception("No managers found")
        formatted = format_user_list(managers)
        manager = print_and_select_from_list(formatted, "Select manager to delete: ")
        manager_id = manager["user_id"]
        delete_employee_from_db(manager_id)
        log_event("manager account deleted", username_enc=session["username_enc"], additional_info=f"manager account deleted (username: {decrypt_value(manager["username_enc"])})")
        return
    log_event("unauthorized manager account delete attempt", username_enc=session["username_enc"], is_suspicious=True)
    raise Exception("Unauthorized access")

def edit_manager_account(session):
    if session["role"] == "manager":
        keys = ["first_name", "last_name"]
        key_to_update = print_and_select_from_list(keys, "Select key to update: ")
        updated_value = go_validate(f"Enter new value for {key_to_update}: ", find_validator(key_to_update))
        updated_value = encrypt_value(updated_value)
        key_to_update = key_to_update + "_enc"
        save_employee_edit(session["user_id"], key_to_update, updated_value)
        log_event("manager account edited", username_enc=session["username_enc"], additional_info=f"manager account edited (username: {decrypt_value(session["username_enc"])}: {key_to_update} updated to {updated_value}")
        return
    log_event("unauthorized manager account edit attempt", username_enc=session["username_enc"], is_suspicious=True)
    raise Exception("Unauthorized access")

def delete_manager_account(session):
    if session["role"] == "manager":
        delete_employee_from_db(session["user_id"])
        log_event("manager account deleted", username_enc=session["username_enc"], additional_info=f"manager account deleted (username: {decrypt_value(session["username_enc"])}")
        return "logout"
    log_event("unauthorized manager account delete attempt", username_enc=session["username_enc"], is_suspicious=True)
    raise Exception("Unauthorized access")

def delete_employee_account(session):
    if session["role"] == "manager":
        employees = fetch_all_employees()
        if not employees:
            raise Exception("No employees found")
        formatted_employees = format_user_list(employees)
        employee = print_and_select_from_list(formatted_employees, "Select employee to delete: ")
        employee_id = employee["user_id"]
        delete_employee_from_db(employee_id)
        log_event("employee account deleted", username_enc=session["username_enc"], additional_info=f"employee account deleted (username: {decrypt_value(employee["username_enc"])} named: {decrypt_value(employee["first_name_enc"])} {decrypt_value(employee["last_name_enc"])}")
        return
    log_event("unauthorized employee account delete attempt", username_enc=session["username_enc"], is_suspicious=True)
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
        log_event("claim deleted", username_enc=session["username_enc"], additional_info=f"claim deleted (id: {claim_id})")
        return
    log_event("unauthorized claim delete attempt", username_enc=session["username_enc"], is_suspicious=True)
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
        log_event("claim edited", username_enc=session["username_enc"], additional_info=f"claim edited (id: {claim_id}): {key_to_update} updated to {updated_value}")
        return
    log_event("unauthorized claim edit attempt", username_enc=session["username_enc"], is_suspicious=True)
    raise Exception("Unauthorized access")

def edit_claim_as_manager_or_admin(session):
    if session["role"] in ["manager", "admin"]:
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
        log_event("claim edited", username_enc=session["username_enc"], additional_info=f"claim edited (id: {claim_id}): {key_to_update} updated to {updated_value}")
        return
    log_event("unauthorized claim edit attempt", username_enc=session["username_enc"], is_suspicious=True)
    raise Exception("Unauthorized access")
    
def find_validator(key_to_update):
    from domain.security.validation import (
        validate_claim_date,
        validate_project_number,
        validate_claim_type,
        validate_travel_distance,
        validate_zip_code,
        validate_house_number,
        validate_name,
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
        "first_name": validate_name,
        "last_name": validate_name,
    }

    if key_to_update not in validators:
        raise Exception(f"No validator found for {key_to_update}")
    return validators[key_to_update]
    
def is_key_value_encrypted(key_to_update):
    if key_to_update in ["travel_distance", "from_zip_code", "to_zip_code", "first_name", "last_name", "email", "mobile_phone", "birthday", "bsn", "street_name", "house_number", "zip_code", "city"]:
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
    if session["role"] in ["manager", "admin"]:
        claims = fetch_pending_claims()
        if not claims:
            raise Exception("No claims found")
        formatted_claims = format_claim_list(claims)
        claim = print_and_select_from_list(formatted_claims, "Select claim to approve: ")
        try: 
            set_claims_salary_batch(session, claim["claim_id"])
            log_event("claims salary batch  set", username_enc=session["username_enc"], additional_info=f"claim (id: {claim["claim_id"]}) salary batch set to {claim["salary_batch"]}")
        except Exception as e:
            raise Exception(f"Error setting salary-batch: {e}")
        save_approved_claim(claim["claim_id"], session["user_id"])
        log_event("claim approved", username_enc=session["username_enc"], additional_info=f"claim approved (id: {claim["claim_id"]})")
        return
    log_event("unauthorized claim approve attempt", username_enc=session["username_enc"], is_suspicious=True)
    raise Exception("Unauthorized access")
    
def reject_claim(session):
    if session["role"] in ["manager", "admin"]:
        claims = fetch_pending_claims()
        if not claims:
            raise Exception("No claims found")
        formatted_claims = format_claim_list(claims)
        claim = print_and_select_from_list(formatted_claims, "Select claim to reject: ")
        save_rejected_claim(claim["claim_id"], session["user_id"])
        log_event("claim rejected", username_enc=session["username_enc"], additional_info=f"claim rejected (id: {claim["claim_id"]})")
        return
    log_event("unauthorized claim reject attempt", username_enc=session["username_enc"], is_suspicious=True)
    raise Exception("Unauthorized access")
    
def format_claim_list(claims): # is this the correct data to display
    return [
        {
            "claim_id": claim["claim_id"],
            "claim_date": claim["claim_date"],
            "claim_type": claim["claim_type"],
            "status": claim["status"],
            "label": (
                f"ID {claim['claim_id']} : {claim['claim_date']} — "
                f"{claim['claim_type']} — {claim['status']}"
            ),
        }
        for claim in claims
    ]

def create_claim(session):
    if session["role"] == "employee":
        claim_data = get_claim_data()
        secured_claim_data = secure_claim_data(session, claim_data)
        save_claim(secured_claim_data)
        log_event("claim created", username_enc=session["username_enc"])
        return
    log_event("unauthorized claim create attempt", username_enc=session["username_enc"], is_suspicious=True)
    raise Exception("Unauthorized access")

def create_user(session):
    log_event("create user attempt", username_enc=session["username_enc"])
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
            log_event("create user success", username_enc=session["username_enc"], additional_info=f"user created: {user_data["username"]}")
            return
        except ValueError as e:
            raise Exception(e)
    log_event("invalid role create user attempt", username_enc=session["username_enc"], is_suspicious=True)
    raise Exception("Invalid role")
    # optionally add visual feedback

def select_manager():
    managers = request_managers()
    if not managers:
        raise Exception("No managers found")
    
    managers_dict = [dict(row) for row in managers]
    managers_names_enc = [manager['first_name_enc'] for manager in managers_dict]
    managers_names = [decrypt_value(name) for name in managers_names_enc]
    manager = print_and_select_from_list(managers_names)
    index = managers_names.index(manager)
    return managers_dict[index]

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
        log_event("employees own claims viewed", username_enc=session["username_enc"]) 
        return
    log_event("unauthorized employees claims view attempt", username_enc=session["username_enc"], is_suspicious=True)
    raise Exception("Unauthorized access")

def request_managers():
    return fetch_all_managers()

def request_employees():
    return fetch_all_employees()

def request_claims(user_id):
    return fetch_all_claims(user_id)

def format_user_list(users):
    return [
        {
            "user_id": employee["user_id"],
            "user": f"{decrypt_value(employee['username_enc'])} : {decrypt_value(employee['first_name_enc'])} {decrypt_value(employee['last_name_enc'])}",
        }
        for employee in users
    ]

def view_employee_list(session):
    if session["role"] == "manager":
        employees = request_employees()
        if not employees:
            raise Exception("No employees found")
        employees_list = format_user_list(employees)    
        print_user_list(employees_list)
        log_event("employee list viewed", username_enc=session["username_enc"])
        return
    log_event("unauthorized employee list view attempt", username_enc=session["username_enc"], is_suspicious=True)
    raise Exception("Unauthorized access")

def view_employees_claims(session):
    if session["role"] == "manager":
        employees = request_employees()
        
        if not employees:
            raise Exception("No employees found")
        
        formatted_employees = format_user_list(employees)
        employee = print_and_select_from_list(formatted_employees, "Select employee: ")
        claims = request_claims(employee["user_id"])
        
        if not claims:
            raise Exception("No claims found")
        
        print_claim_list(claims)
        log_event("employees claims viewed", username_enc=session["username_enc"], additional_info=f"employee: {decrypt_value(employee["username_enc"])} claims viewed")
        return
    log_event("unauthorized employees claims view attempt", username_enc=session["username_enc"], is_suspicious=True)
    raise Exception("Unauthorized access")