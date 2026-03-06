from domain.utils import secure_user_data
from infrastructure.database import init_db, save_user, username_exists
from presentation.cli import get_create_user_input

def app():
    init_db()
    login()

def login(): pass

def create_user(username):
    user = get_create_user_input()
    
    # these func's require DB connection
    verify_username(user["username"])
    
    secured_user = secure_user_data(user)
    save_user(secured_user)

def verify_username(username): 
    if username_exists(username):
        raise ValueError("Username already exists")

def verify_password(password): pass

    