from domain.security.hashing import verify_restore_code
from infrastructure.backup_infrastructure import fetch_all_backups
from infrastructure.database import fetch_all_employees, fetch_all_managers, fetch_all_restore_codes
from presentation.helpers import input_restore_code, print_and_select_from_list
from domain.security.encryption import decrypt_value

def select_manager():
    managers = request_managers()
    if not managers:
        raise Exception("No managers found")
    managers_names = [decrypt_value(manager) for manager in managers]
    manager = print_and_select_from_list(managers_names)
    index = managers_names.index(manager)
    return managers[index]

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


def request_managers():
    return fetch_all_managers()

def request_employees():
    return fetch_all_employees()

def format_employee_list(employees):
    return [{"id": employee["user_id"], "name": f"{decrypt_value(employee['first_name_enc'])} {decrypt_value(employee['last_name_enc'])}"} for employee in employees]

def view_employee_list(session):
    employees = request_employees()
    if not employees:
        raise Exception("No employees found")
    employees_list = format_employee_list(employees)
    return print_and_select_from_list(employees_list)