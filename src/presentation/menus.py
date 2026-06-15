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

def _run_menu(options, session):
    while True:
        print(generate_menu_title(session))
        for i, (label, action) in enumerate(options, 1):
            print(f"  {i}. {label}")
        choice = go_validate_menu_choice("Choice: ", validate_menu_choice, len(options))
        if choice is None:
            print_error("Invalid choice")
            continue
        try:
            idx = int(choice) - 1
            label, action = options[idx]
            if action == "logout":
                return "logout"
            if action == "exit":
                return "exit"
            if callable(action):
                try:
                    result = action(session)
                    if result == "logout":
                        return "logout"
                    if result == "exit":
                        return "exit"
                except Exception as e:
                    if str(e) == "Unauthorized access":
                        return "logout"
                    log_event("menu action crash", is_suspicious=True)
                    print_error("An unexpected error occurred.")
        except:
            print_error("Invalid input format")
            continue

def superadmin_menu(session):
    if session["role"] != "admin":
        log_event("unauthorized_menu_access", username_enc=session["username_enc"], is_suspicious=True)
        return "logout"

    options = [
        ("Create manager account", create_user),
        ("Backup system", call_to_create_backup),
        ("Generate restore code for manager", assign_backup),
        ("Restore any backup", restore_any_backup),
        ("View restore code status", view_restore_code_status),
        ("Revoke restore code", revoke_restore_code),
        ("Edit pending claims project/travel distance", edit_claim_as_manager_or_admin),
        ("Approve claim", approve_claim),
        ("Reject claim", reject_claim),
        ("Search claim", search_claims),
        ("Search employee", search_employees),
        ("Update manager account", edit_manager_account_as_admin),
        ("Delete manager account", delete_manager_account_as_admin),
        ("Reset users password", reset_users_password),
        ("View logs", view_logs),
        ("Logout", "logout"),
        ("Exit system", "exit"),
    ]

    return _run_menu(options, session)

def manager_menu(session):
    if session["role"] != "manager":
        log_event("unauthorized_menu_access", username_enc=session["username_enc"], is_suspicious=True)
        return "logout"

    options = [
        ("Search claim", search_claims),
        ("Search employee", search_employees),
        ("Create employee account", create_user),
        ("Edit employee account", edit_employee_account),
        ("Delete employee account", delete_employee_account),
        ("Reset employee password", reset_users_password),
        ("Backup system", call_to_create_backup),
        ("Restore backup with code", restore_backup_with_code),
        ("View employee list", view_employee_list),
        ("View claims submitted by employees", view_employees_claims),
        ("Edit pending claims project/travel distance", edit_claim_as_manager_or_admin),
        ("Approve claim", approve_claim),
        ("Reject claim", reject_claim),
        ("View logs", view_logs),
        ("Update my password", update_password),
        ("Update my account", edit_manager_account),
        ("Delete my account", delete_manager_account),
        ("Logout", "logout"),
        ("Exit system", "exit"),
    ]

    return _run_menu(options, session)


def employee_menu(session):
    if session["role"] != "employee":
        log_event("unauthorized_menu_access", username_enc=session["username_enc"], is_suspicious=True)
        return "logout"

    options = [
        ("Search in my claims", search_claims),
        ("Submit new claim", create_claim),
        ("View own claims", request_employees_claims),
        ("Edit my claim", edit_claim),
        ("Delete my claim", delete_claim),
        ("Update my password", update_password),
        ("Logout", "logout"),
        ("Exit system", "exit"),
    ]

    return _run_menu(options, session)

def generate_menu_title(session):
    if session["role"] == "admin":
        return f"\n--- Super Admin ({unread_suspicious_log_count()} unread suspicious logs) ---"
    elif session["role"] == "manager":
        return f"\n--- Manager ({unread_suspicious_log_count()} unread suspicious logs) ---"
    elif session["role"] == "employee":
        return "\n--- Employee ---"
