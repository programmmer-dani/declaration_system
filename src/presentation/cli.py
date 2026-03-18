# Add input validation
# 
def get_login_input():
    username = input("Username: ")
    password = input("Password: ")
    return {"username": username, "password": password}


def get_user_data():
    print("\nCreating new user...\n")
    user_data = {
        "username": input("Username: "),
        "password": input("Password: "),
        "first_name": input("First name: "),
        "last_name": input("Last name: "),
        "role": input("Role (manager/employee): "),
    }
    if user_data["role"] == "employee":
        employee_data = get_employee_data()
        return {**user_data, **employee_data}
    else:
        return user_data
    
def get_employee_data():    
    return {
        "birthday": input("Birthday: "),
        "gender": input("Gender: "),
        "street_name": input("Street name: "),
        "house_number": input("House number: "),
        "zip_code": input("Zip code: "),
        "city": input("City: "),
        "email": input("Email: "),
        "mobile_phone": input("Mobile phone: "),
        "id_doc_type": input("ID doc type: "),
        "id_doc_number": input("ID doc number: "),
        "bsn": input("BSN: "),
    }


def print_error(error):
    print(f"\n-----------------\nError: {error}\n-----------------\n")

def _run_menu(title, options, session):
    """Display menu and loop until user picks the last option (logout/exit). options: list of (label, callable or None)."""
    while True:
        print(f"\n--- {title} ---")
        for i, (label, _) in enumerate(options, 1):
            print(f"  {i}. {label}")
        choice = input("Choice: ").strip() # create seperate menu input functionality
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(options):
            print("Invalid option.")
            continue
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