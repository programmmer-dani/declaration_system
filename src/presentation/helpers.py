import datetime

from logging_system import log_event
from domain.security.encryption import decrypt_value
from domain.security.validation import validate_birthday, validate_bsn, validate_city, validate_claim_date, validate_email, validate_employee_search_term, validate_gender, validate_house_number, validate_id_doc_number, validate_id_doc_type, validate_menu_choice, validate_mobile_phone, validate_name, validate_password, validate_restore_code, validate_street_name, validate_username, validate_zip_code
from infrastructure.backup_infrastructure import create_backup
from domain.security.validation import (
    validate_claim_date,
    validate_claim_search_term,
    validate_claim_type,
    validate_project_number,
    validate_travel_distance,
    validate_zip_code,
    validate_house_number,
)

def get_login_input():
    username = go_validate("Username: ", validate_username)
    password = go_validate("Password: ", validate_password)
    log_event("login attempt")
    return {"username": username, "password": password}

def print_error(error):
    print(f"\n-----------------\nError: {error}\n-----------------\n")

    
def go_validate(input_message, validator):
    while True:
        value = input(input_message)
        if validator(value):
            return value
        print_error("Invalid input, try again.")

def go_validate_menu_choice(input_message, validator, number_of_choices):
    while True:
        value = input(input_message)
        if validator(value, number_of_choices):
            return value
        print_error("Invalid input, try again.")

def _menu_line(item):
    if isinstance(item, dict):
        if "user" in item:
            return item["user"]
        if "label" in item:
            return item["label"]
    return str(item)


def print_and_select_from_list(list, message="Choose item: "):
    for i, item in enumerate(list, 1):
        print(f"{i}. {_menu_line(item)}")
    choice = go_validate_menu_choice(message, validate_menu_choice, len(list))
    return list[int(choice) - 1]

def print_user_list(users):
    for i, user in enumerate(users, 1):
        if isinstance(user, dict) and "user" in user:
            print(f"{i}. {user['user']}")
        else:
            print(f"{i}. {user['first_name']} {user['last_name']}")
        
def print_temp_password(temp_password):
    print(f"Temporary password: {temp_password}")
        
def print_claim_list(claims): # is this the correct data to display
    print("Your claims: ")
    for claim in claims:
        print(
            f"ID {claim['claim_id']} : {claim['claim_date']} — "
            f"{claim['claim_type']} — {claim['status']}"
        )


def _format_log_created_at(created_at):
    log_stored_ts = "%Y%m%d_%H%M%S"
    log_display_ts = "%Y-%m-%d %H:%M:%S"
    try:
        return datetime.datetime.strptime(created_at, log_stored_ts).strftime(log_display_ts)
    except (ValueError, TypeError):
        return str(created_at)


def print_log_list(logs):
    for row in logs:
        r = dict(row)
        when = _format_log_created_at(r["created_at"])
        act = decrypt_value(r["activity_desc_enc"])
        user = decrypt_value(r["username_enc"]) if r["username_enc"] is not None else "—"
        extra = decrypt_value(r["additional_info_enc"]) if r["additional_info_enc"] else "—"
        susp = "yes" if r["is_suspicious"] else "no"
        read = "yes" if r["is_read"] else "no"
        print(
            f"[{r['log_id']}] {when} | {act} | username={user} | additional_info={extra} "
            f"| is_suspicious={susp} | is_read={read}"
        )


def call_to_create_backup(session):
    if session["role"] in ["admin", "manager"]:
        print("Creating backup...")
        log_event("backup created from this point", username_enc=session["username_enc"])
        backup_path = create_backup() # presentation layer shouldn't make this call, domain logic should
        print(f"Backup created at {backup_path}")
        return
    log_event("unauthorized backup create attempt", username_enc=session["username_enc"], is_suspicious=True)
    raise Exception("Unauthorized access")
    
    
    
def input_claim_search_term():
    return go_validate(
        "Search claim: ",
        validate_claim_search_term,
    )

def input_employee_search_term():
    return go_validate(
        "Search employee: ",
        validate_employee_search_term,
    )

def input_restore_code():
    restore_code = go_validate("Restore code: ", validate_restore_code)
    return restore_code
    
def display_restorecode_status(used, revoked):
    print(f"Restore code status:")
    if used == 1:
        print(f"Used: Yes")
    else:
        print(f"Used: No")
    if revoked == 1:
        print(f"Revoked: Yes")
    else:
        print(f"Revoked: No")
        
        
def get_claim_data():
    print("\nCreating new claim...\n")

    claim_data = {
        "claim_date": go_validate("Claim date (YYYY-MM-DD): ", validate_claim_date),
        "project_number": go_validate("Project number: ", validate_project_number),
        "claim_type": go_validate("Claim type (Travel/Home Office): ", validate_claim_type),
    }

    if claim_data["claim_type"] == "Travel":
        travel_data = get_travel_claim_data()
        return {**claim_data, **travel_data}

    return claim_data


def get_travel_claim_data():
    return {
        "travel_distance": go_validate("Travel distance in km: ", validate_travel_distance),
        "from_zip_code": go_validate("From ZIP code: ", validate_zip_code),
        "from_house_number": go_validate("From house number: ", validate_house_number),
        "to_zip_code": go_validate("To ZIP code: ", validate_zip_code),
        "to_house_number": go_validate("To house number: ", validate_house_number),
    }        

def get_user_data(role):
    print("\nCreating new user...\n")
    user_data = {
        "username": go_validate("Username: ", validate_username),
        "password": go_validate("Password: ", validate_password),
        "first_name": go_validate("First name: ", validate_name),
        "last_name": go_validate("Last name: ", validate_name),
        "role": role,
    }
    if user_data["role"] == "employee":
        employee_data = get_employee_data()
        return {**user_data, **employee_data}
    else:
        return user_data
    
def get_employee_data():    
    return {
        "birthday": go_validate("Birthday (YYYY-MM-DD): ", validate_birthday),
        "gender": go_validate("Gender (male/female): ", validate_gender),
        "street_name": go_validate("Street name: ", validate_street_name),
        "house_number": go_validate("House number: ", validate_house_number),
        "zip_code": go_validate("Zip code: ", validate_zip_code),
        "city": go_validate("City: ", validate_city),
        "email": go_validate("Email: ", validate_email),
        "mobile_phone": go_validate("Mobile phone (8 digits): ", validate_mobile_phone),
        "id_doc_type": go_validate("ID doc type (Passport/ID-Card): ", validate_id_doc_type),
        "id_doc_number": go_validate("ID doc number: ", validate_id_doc_number),
        "bsn": go_validate("BSN: ", validate_bsn),
    }