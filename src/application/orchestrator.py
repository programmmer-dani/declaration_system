from domain.utils import print_db_content, secure_user_data
from infrastructure.database import init_db, save_user, username_exists
from presentation.cli import get_create_user_input, get_login_input, print_error

def app():
    init_db()
    login(get_login_input())

def login(credentials): 
    if credentials["username"] == "super_admin" and credentials["password"] == "Admin_123?":
        try: create_user(get_create_user_input())
        except ValueError as e:
            print_error(e)

def create_user(user):
    try:
        verify_existing_username(user["username"])
        secured_user_data = secure_user_data(user)
        save_user(secured_user_data)
        print_db_content()
    except ValueError as e:
        return e

def verify_existing_username(username): 
    if username_exists(username):
        raise ValueError("Username already exists")

def verify_password(password): pass