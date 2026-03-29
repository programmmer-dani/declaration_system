
from domain.backup_logic import list_backups
from domain.security.validation import validate_menu_choice, validate_password, validate_username


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
    