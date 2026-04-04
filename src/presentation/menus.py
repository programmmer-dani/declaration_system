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
    search_claims,
    search_employees,
    set_claims_salary_batch,
    update_password,
    view_employee_list,
    view_employees_claims,
    view_logs,
)
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
### LOGGING FUNCTIONALITY MADE BUT NEEDS TO BE CALLED ON THE APPROPRIATE PLACES

def superadmin_menu(session):
    if session["role"] != "admin":
        return Exception("Unauthorized access")
    unread_logs = uread_log_count()
    return _run_menu(f"Super Admin ({unread_logs} unread suspicious logs)", [
        ("Create manager account", create_user), # does manager create employee account?????????
        ("Backup system", call_to_create_backup), # now displays complete filepath of where backup is saved??? vulnerable to path traversal attack
        ("Generate restore code for manager", assign_backup), # NEEDS TESTING errror: token must be bytes or string
        ("Restore any backup", restore_any_backup), # add visual feedback for completing task (optional)
        ("View restore code status", view_restore_code_status), # NEEDS TESTING
        ("Revoke restore code", revoke_restore_code), # NEEDS TESTING fake restore codes get: 'NoneType' object is not subscriptable
        ("Edit claims project/travel distance", edit_claim_as_manager_or_admin), # NEEDS TESTING
        ("Approve claim", approve_claim), # NEEDS TESTING
        ("Reject claim", reject_claim), # NEEDS TESTING
        ("Assign claim to salary-batch", set_claims_salary_batch), # NEEDS TESTING
        ("Search claim", search_claims),
        ("Search employee", search_employees),
        ("Update manager account", edit_manager_account_as_admin), # NEEDS TESTING
        ("Delete manager account", delete_manager_account_as_admin), # NEEDS TESTING
        ("Reset employee password", None),
        ("Reset manager password", None),
        ("View logs", view_logs), # on hold till logging is made complete
        ("Logout", None),
        ("Exit system", None),
    ], session)


def manager_menu(session):
    if session["role"] != "manager":
        return Exception("Unauthorized access")
    unread_logs = uread_log_count()
    return _run_menu(f"Manager ({unread_logs} unread suspicious logs)", [ # Check if count updates automatically (I think it does)
        ("Search claim", search_claims),
        ("Search employee", search_employees),
        ("Create employee account", create_user),
        ("Edit employee account", edit_employee_account),
        ("Delete employee account", delete_employee_account),
        ("reset employee password", None),
        ("Backup system", call_to_create_backup),
        ("Restore backup with code", restore_backup_with_code), # NEEDS TESTING
        ("View employee list", view_employee_list), # NEEDS TESTING
        ("View claims submitted by employees", view_employees_claims), # NEEDS TESTING
        ("Edit claims project/travel distance", edit_claim_as_manager_or_admin), # NEEDS TESTING
        ("Assign claim to salary-batch", set_claims_salary_batch), # NEEDS TESTING
        ("Approve claim", approve_claim), # NEEDS TESTING
        ("Reject claim", reject_claim), # NEEDS TESTING
        ("View logs", view_logs), # on hold till logging is made complete
        ("Update my password", update_password), # NEEDS TESTING
        ("Update my account", edit_manager_account), # NEEDS TESTING
        ("Delete my account", delete_manager_account), # NEEDS TESTING
        ("Logout", None),
        ("Exit system", None),
    ], session)


def employee_menu(session):
    if session["role"] != "employee":
        return Exception("Unauthorized access")
    return _run_menu("Employee", [
        ("Search in my claims", search_claims),
        ("Submit new claim", create_claim),
        ("View own claims", request_employees_claims), # NEEDS TESTING
        ("Edit my claim", edit_claim),# NEEDS TESTING
        ("Delete my claim", delete_claim),# NEEDS TESTING
        ("Update my password", update_password), # NEEDS TESTING
        ("Logout", None),
        ("Exit system", None),
    ], session)
    
    
# NEXT STEPS:
# - RESET PASSWORD FUNCTIONALITY
# - IMPLEMENT COMPLETE LOGGING WHERE NEEDED (functionality already made)
# - TEST ALL FUNCTIONALITY EXTENSIVELY