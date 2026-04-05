from domain.backup_logic import assign_backup, restore_any_backup, restore_backup_with_code, revoke_restore_code, view_restore_code_status
from domain.helpers import (
    approve_claim,
    create_claim,
    create_user,
    delete_claim,
    delete_employee_account,
    delete_manager_account,
    delete_manager_account_as_admin,
    edit_claim,
    edit_claim_as_manager_or_admin,
    edit_employee_account,
    edit_manager_account,
    edit_manager_account_as_admin,
    reject_claim,
    request_employees_claims,
    reset_users_password,
    search_claims,
    search_employees,
    update_password,
    view_employee_list,
    view_employees_claims,
    view_logs,
)
from domain.security.validation import validate_menu_choice
from logging_system import log_event, unread_suspicious_log_count
from presentation.helpers import call_to_create_backup, go_validate_menu_choice, print_error

def _run_menu(title, options, session):
    print(f"\n--- {title} ---")
    for i, (label, _) in enumerate(options, 1):
        print(f"  {i}. {label}")
    choice = go_validate_menu_choice("Choice: ", validate_menu_choice, len(options))
    if choice is None:
        print_error("Invalid choice")
        return
    idx = int(choice) - 1
    if idx == len(options) - 2:
        session = None
        return "logout"
    if idx == len(options) - 1:
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
        
def superadmin_menu(session):
    if session["role"] != "admin":
        log_event("unauthorized menu access attempt", username_enc=session["username"], is_suspicious=True)
        return Exception("Unauthorized access")
    unread_logs = unread_suspicious_log_count()
    return _run_menu(f"Super Admin ({unread_logs} unread suspicious logs)", [
        ("Create manager account", create_user),
        ("Backup system", call_to_create_backup),
        ("Generate restore code for manager", assign_backup),
        ("Restore any backup", restore_any_backup),
        ("View restore code status", view_restore_code_status),
        ("Revoke restore code", revoke_restore_code),
        ("Edit claims project/travel distance", edit_claim_as_manager_or_admin),
        ("Approve claim", approve_claim),
        ("Reject claim", reject_claim),
        ("Search claim", search_claims),
        ("Search employee", search_employees),
        ("Update manager account", edit_manager_account_as_admin),
        ("Delete manager account", delete_manager_account_as_admin),
        ("Reset users password", reset_users_password),
        ("View logs", view_logs),
        ("Logout", None),
        ("Exit system", None),
    ], session)


def manager_menu(session):
    if session["role"] != "manager":
        log_event("unauthorized menu access attempt", username_enc=session["username"], is_suspicious=True)
        return Exception("Unauthorized access")
    unread_logs = unread_suspicious_log_count()
    return _run_menu(f"Manager ({unread_logs} unread suspicious logs)", [
        ("Search claim", search_claims),
        ("Search employee", search_employees),
        ("Create employee account", create_user),
        ("Edit employee account", edit_employee_account),
        ("Delete employee account", delete_employee_account),
        ("reset employee password", reset_users_password),
        ("Backup system", call_to_create_backup),
        ("Restore backup with code", restore_backup_with_code),
        ("View employee list", view_employee_list),
        ("View claims submitted by employees", view_employees_claims),
        ("Edit claims project/travel distance", edit_claim_as_manager_or_admin),
        ("Approve claim", approve_claim),
        ("Reject claim", reject_claim),
        ("View logs", view_logs),
        ("Update my password", update_password),
        ("Update my account", edit_manager_account),
        ("Delete my account", delete_manager_account),
        ("Logout", None),
        ("Exit system", None),
    ], session)


def employee_menu(session):
    if session["role"] != "employee":
        log_event("unauthorized menu access attempt", username_enc=session["username"], is_suspicious=True)
        return Exception("Unauthorized access")
    return _run_menu("Employee", [
        ("Search in my claims", search_claims),
        ("Submit new claim", create_claim),
        ("View own claims", request_employees_claims),
        ("Edit my claim", edit_claim),
        ("Delete my claim", delete_claim),
        ("Update my password", update_password),
        ("Logout", None),
        ("Exit system", None),
    ], session)