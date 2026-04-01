from domain.backup_logic import assign_backup, restore_any_backup, restore_backup_with_code, revoke_restore_code, view_restore_code_status
from domain.security.validation import (
    validate_birthday,
    validate_bsn,
    validate_city,
    validate_email,
    validate_gender,
    validate_house_number,
    validate_id_doc_number,
    validate_id_doc_type,
    validate_menu_choice,
    validate_mobile_phone,
    validate_name,
    validate_password,
    validate_role,
    validate_street_name,
    validate_username,
    validate_zip_code,
)
from presentation.helpers import call_to_create_backup, go_validate, go_validate_menu_choice, print_error

def get_user_data():
    print("\nCreating new user...\n")
    user_data = {
        "username": go_validate("Username: ", validate_username),
        "password": go_validate("Password: ", validate_password),
        "first_name": go_validate("First name: ", validate_name),
        "last_name": go_validate("Last name: ", validate_name),
        "role": go_validate("Role (manager/employee): ", validate_role),
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

def _run_menu(title, options, session):
    print(f"\n--- {title} ---")
    for i, (label, _) in enumerate(options, 1):
        print(f"  {i}. {label}")
    choice = go_validate_menu_choice("Choice: ", validate_menu_choice, len(options))
    if choice is None:
        print_error("Invalid choice") # dead code
        return
    idx = int(choice) - 1
    if idx == len(options) - 2:  # logout
        session = None
        return "logout"
    if idx == len(options) - 1:  # exit system
        return "exit"
    execute_option = options[idx][1]
    if execute_option:
        try:
            result = execute_option(session)
            if result == "logout":
                return "logout"
            if result == "exit":
                return "exit"
        except Exception as e:
            print_error(e)
            return
    else:
        print("Not implemented yet.")
        

### ALL MENU FUNCTIONALITIES NEED SESSION PARAMETER, FIX THIS (so that they expect this parameter)

def superadmin_menu(session):
    if session["role"] != "admin":
        return Exception("Unauthorized access")
    return _run_menu("Super Admin", [
        ("Create manager account", None),
        ("Backup system", call_to_create_backup),
        ("Generate restore code for manager", assign_backup), # NEEDS TESTING
        ("Restore any backup", restore_any_backup), # add visual feedback for completing task (optional)
        ("View restore code status", view_restore_code_status), # NEEDS TESTING
        ("Revoke restore code", revoke_restore_code), # NEEDS TESTING
        ("Logout", None),
        ("Exit system", None),
    ], session)


def manager_menu(session):
    if session["role"] != "manager":
        return Exception("Unauthorized access")
    return _run_menu("Manager", [
        ("Create employee account", None),
        ("Backup system", call_to_create_backup),
        ("Restore backup with code", restore_backup_with_code), # NEEDS TESTING
        ("View employee list", None), # do next
        ("View claims submitted by employees", None), # do next
        ("Approve claim", None),
        ("Reject claim", None),
        ("Logout", None),
        ("Exit system", None),
    ], session)


def employee_menu(session):
    if session["role"] != "employee":
        return Exception("Unauthorized access")
    return _run_menu("Employee", [
        ("Submit new claim", None),
        ("View own claims", None),
        ("Edit claim", None),
        ("Delete claim", None),
        ("Logout", None),
        ("Exit system", None),
    ], session)