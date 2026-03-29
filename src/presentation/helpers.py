from operator import indexOf
from turtle import back
from domain.core_functionality import list_backups
from domain.security.validation import validate_menu_choice


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
    for name in backup_names:
        i = indexOf(name)+1
        print(f"{i}. name")
        
def select_backup():
    backups = list_backups()
    view_all_backups(backups)
    
    try: 
        backup_name = backups[go_validate_menu_choice("Choose backup to restore: ", validate_menu_choice, backups.length())]
    except Exception as e: 
        print_error(e)
        
    if backup_name: 
        return backup_name
    
    