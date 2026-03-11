from domain.security.security import login
from infrastructure.database import init_db
from presentation.cli import get_login_input, print_error

def app():
    init_db()
    session = login(get_login_input())
    while session is None:
        print_error("Invalid username or password")
        session = login(get_login_input())
        # display_menu(session)

