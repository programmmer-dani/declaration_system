from domain.security.security import login, verify_user_menu
from infrastructure.database import init_db
from presentation.cli import get_login_input, print_error

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
    if menu and session: # whitelisting instead of blacklisting
        menu(session)
        exit()
        
    app()