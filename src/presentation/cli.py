from domain.security.validation import (
    validate_birthday,
    validate_bsn,
    validate_city,
    validate_email,
    validate_gender,
    validate_house_number,
    validate_id_doc_number,
    validate_id_doc_type,
    validate_mobile_phone,
    validate_name,
    validate_password,
    validate_role,
    validate_street_name,
    validate_username,
    validate_zip_code,
)


def _go_validate(input_message, validator):
    while True:
        value = input(input_message)
        if validator(value):
            return value
        print("Invalid input, try again.")


def get_login_input():
    username = _go_validate("Username: ", validate_username)
    password = _go_validate("Password: ", validate_password)
    return {"username": username, "password": password}


def get_user_data():
    print("\nCreating new user...\n")
    user_data = {
        "username": _go_validate("Username: ", validate_username),
        "password": _go_validate("Password: ", validate_password),
        "first_name": _go_validate("First name: ", validate_name),
        "last_name": _go_validate("Last name: ", validate_name),
        "role": _go_validate("Role (manager/employee): ", validate_role),
    }
    if user_data["role"] == "employee":
        employee_data = get_employee_data()
        return {**user_data, **employee_data}
    else:
        return user_data
    
def get_employee_data():    
    return {
        "birthday": _go_validate("Birthday (YYYY-MM-DD): ", validate_birthday),
        "gender": _go_validate("Gender (male/female): ", validate_gender),
        "street_name": _go_validate("Street name: ", validate_street_name),
        "house_number": _go_validate("House number: ", validate_house_number),
        "zip_code": _go_validate("Zip code: ", validate_zip_code),
        "city": _go_validate("City: ", validate_city),
        "email": _go_validate("Email: ", validate_email),
        "mobile_phone": _go_validate("Mobile phone (8 digits): ", validate_mobile_phone),
        "id_doc_type": _go_validate("ID doc type (Passport/ID-Card): ", validate_id_doc_type),
        "id_doc_number": _go_validate("ID doc number: ", validate_id_doc_number),
        "bsn": _go_validate("BSN: ", validate_bsn),
    }


def print_error(error):
    print(f"\n-----------------\nError: {error}\n-----------------\n")

def _run_menu(title, options, session):
    while True:
        print(f"\n--- {title} ---")
        for i, (label, _) in enumerate(options, 1):
            print(f"  {i}. {label}")
        choice = input("Choice: ").strip() # create seperate menu input functionality
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(options):
            print("Invalid option.")
        else:
            idx = int(choice) - 1
            if idx == len(options) - 1: # last function is always log out or exit
                return # Logout should be handled differently then exit tho
            execute_option = options[idx][1]
            if execute_option:
                execute_option(session)
            else:
                print("Not implemented yet.")


def superadmin_menu(session):
    if session["role"] != "admin":
        return Exception("Unauthorized access")
    _run_menu("Super Admin", [
        ("Create manager account", None),
        ("Generate restore code for manager", None),
        ("Restore database from backup", None),
        ("View restore code status", None),
        ("Revoke restore code", None),
        ("Exit system", None),
    ], session)


def manager_menu(session):
    if session["role"] != "manager":
        return Exception("Unauthorized access")
    _run_menu("Manager", [
        ("Create employee account", None),
        ("View employee list", None),
        ("View claims submitted by employees", None),
        ("Approve claim", None),
        ("Reject claim", None),
        ("Generate database backup", None),
        ("Logout", None),
    ], session)


def employee_menu(session):
    if session["role"] != "employee":
        return Exception("Unauthorized access")
    _run_menu("Employee", [
        ("Submit new claim", None),
        ("View own claims", None),
        ("Edit claim", None),
        ("Delete claim", None),
        ("Logout", None),
    ], session)