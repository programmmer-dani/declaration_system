from domain.core_functionality import list_backups
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
        
def view_all_backups(backup_names):
    for i, name in enumerate(backup_names, 1):
        print(f"{i}. {name}")


def select_backup():
    backups = list_backups()
    if not backups:
        print_error("No backups available.")
        return None
    view_all_backups(backups)
    choice = go_validate_menu_choice(
        "Choose backup to restore: ", validate_menu_choice, len(backups)
    )
    return backups[int(choice) - 1]

    