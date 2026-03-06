from infrastructure.database import username_exists
from presentation.cli import get_create_user_input

def app():
    login()

def login(): pass

def create_user(username):
    user = get_create_user_input()
    if username_exists(user.username):
        raise ValueError("Username already exists")
    