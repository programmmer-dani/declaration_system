from domain.security.bruteforece_detection import is_bruteforce_lockout_active
from domain.security.security import login
from infrastructure.database import init_db
from logging_system import log_event
from presentation.helpers import get_login_input, print_error
from presentation.menus import employee_menu, manager_menu, superadmin_menu


def app():
    init_db()

    if is_bruteforce_lockout_active():
        print_error("Too many failed login attempts. Please wait about one minute.")
        exit()

    session = login(get_login_input())

    while session is None:
        print_error("Invalid username or password")
        if is_bruteforce_lockout_active():
            log_event("bruteforce lockout activated", is_suspicious=True)
            print_error("Too many failed login attempts. Please wait about one minute.")
            exit()
        session = login(get_login_input())
        
    try:
        menu = verify_user_menu(session)
        
    except Exception as e:
        session = None
        print_error(e)
        app()
    
    while menu and session:
        try: running = menu(session)
        except Exception as e:
            print_error(e)
            session = None
            app()
        if running == "logout":
            session = None
            app()
        if running == "exit":
            exit()
    exit()
    
    
def verify_user_menu(session):
    if session["role"] == "admin":
        return superadmin_menu
    elif session["role"] == "manager":
        return manager_menu
    elif session["role"] == "employee":
        return employee_menu
    log_event("unexisting role login attempt", username_enc=session["username"], is_suspicious=True)
    raise Exception("Invalid role")