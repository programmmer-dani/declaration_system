import datetime
from datetime import UTC
from domain.utils import hash_password, secure_user_data
from infrastructure.database import find_user_by_username, init_db, save_user, username_exists
from presentation.cli import get_login_input, print_error

def app():
    init_db()
    session = login(get_login_input())
    while session is None:
        print_error("Invalid username or password")
        session = login(get_login_input())

def login(credentials): 
    if credentials["username"] == "super_admin" and credentials["password"] == "Admin_123?":
        return {"role":"super_admin"}
    user = find_user_by_username(credentials["username"])
    if user is None:
        return None
    if verify_password(credentials["password"]) == user["password"]:
        return user
    return None
    

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

def verify_password(inputed_password, stored_password):
    return hash_password(inputed_password) == stored_password