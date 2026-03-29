from domain.security.security import login, verify_user_menu
from infrastructure.database import init_db
from presentation.menus import get_login_input, print_error

def app():
    init_db()
    
    session = login(get_login_input())
    
    while session is None:
        print_error("Invalid username or password")
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