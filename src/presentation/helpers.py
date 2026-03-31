from domain.security.validation import validate_menu_choice, validate_password, validate_restore_code, validate_username
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
    
def call_to_create_backup(session):
    print("Creating backup...")
    backup_path = create_backup() # presentation layer shouldn't make this call, domain logic should
    print(f"Backup created at {backup_path}")
    
    
def  input_restore_code():
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