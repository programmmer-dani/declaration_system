import datetime
from datetime import UTC
from domain.utils import print_db_content, secure_employee_data, secure_user_data
from infrastructure.database import init_db, save_user, username_exists
from presentation.cli import get_employee_data, get_login_input, get_user_data, print_error

def app():
    init_db()
    login(get_login_input())

def login(credentials): 
    if credentials["username"] == "super_admin" and credentials["password"] == "Admin_123?":
        try: create_user(get_user_data())
        except ValueError as e:
            print_error(e)

def create_user(user_data):
    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S")
    try:
        verify_existing_username(user_data["username"])
        secured_user_data = secure_user_data(user_data) 
        save_user(now, secured_user_data)
    except ValueError as e:
        return e

def verify_existing_username(username): 
    if username_exists(username):
        raise ValueError("Username already exists")

def verify_password(password): pass