from time import time

from domain.security.bruteforece_detection import is_bruteforce_lockout_active
from domain.security.security import login
from infrastructure.database import init_db
from logging_system import log_event
from presentation.helpers import get_login_input, print_error
from presentation.menus import employee_menu, manager_menu, superadmin_menu

def app():
    init_db()
    
    while True:
        if is_bruteforce_lockout_active():
            print_error("Too many failed attempts. System locked for 1 minute.")
            time.sleep(60)
            continue

        session = login()
        
        if session:
            result = verify_user_menu(session)
            
            if result == "logout":
                print("Logged out.")
                continue
            elif result == "exit":
                print("Exiting application...")
                exit()
        else:
            print_error("Invalid username or password")

    
def verify_user_menu(session):
    if session["role"] == "admin":
        return superadmin_menu(session)
    elif session["role"] == "manager":
        return manager_menu(session)
    elif session["role"] == "employee":
        return employee_menu(session)
    log_event("unexisting role login attempt", username_enc=session["username"], is_suspicious=True)
    return "logout"
