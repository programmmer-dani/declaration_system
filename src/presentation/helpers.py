from domain.security.validation import validate_birthday, validate_bsn, validate_city, validate_email, validate_gender, validate_house_number, validate_id_doc_number, validate_id_doc_type, validate_menu_choice, validate_mobile_phone, validate_name, validate_password, validate_restore_code, validate_role, validate_street_name, validate_username, validate_zip_code
from infrastructure.backup_infrastructure import create_backup

def get_login_input():
    username = go_validate("Username: ", validate_username)
    password = go_validate("Password: ", validate_password)
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

def print_and_select_from_list(list):
    for i, item in enumerate(list, 1):
        print(f"{i}. {item}")
    choice = go_validate_menu_choice("Choose item: ", validate_menu_choice, len(list))
    return list[int(choice) - 1]

def print_employee_list(employees):
    for i, employee in employees:
        print(f"{i}. {employee['name']}")
        
def print_claim_list(claims, employee_name):
    print(f"Claims for {employee_name}:")
    for i, claim in claims:
        print(f"ID {claim['claim_id']} : {claim['claim_date']} - {claim['claim_amount']} - {claim['claim_status']}")
    
def call_to_create_backup(session):
    print("Creating backup...")
    backup_path = create_backup() # presentation layer shouldn't make this call, domain logic should
    print(f"Backup created at {backup_path}")
    
    
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