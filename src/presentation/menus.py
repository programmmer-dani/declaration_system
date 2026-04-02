from domain.backup_logic import assign_backup, restore_any_backup, restore_backup_with_code, revoke_restore_code, view_restore_code_status
from domain.helpers import view_employee_list, view_employees_claims
from domain.security.validation import validate_menu_choice
from logging_system import uread_log_count
from presentation.helpers import call_to_create_backup, go_validate_menu_choice, print_error

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
    unread_logs = uread_log_count()
    return _run_menu(f"Super Admin ({unread_logs} unread logs)", [
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
    unread_logs = uread_log_count()
    return _run_menu(f"Manager ({unread_logs} unread logs)", [
        ("Create employee account", None),
        ("Backup system", call_to_create_backup),
        ("Restore backup with code", restore_backup_with_code), # NEEDS TESTING
        ("View employee list", view_employee_list), # NEEDS TESTING
        ("View claims submitted by employees", view_employees_claims), # NEEDS TESTING
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