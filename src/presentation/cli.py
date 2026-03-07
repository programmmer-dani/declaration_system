# Add input validation


def get_login_input():
    username = input("Username: ")
    password = input("Password: ")
    return {"username": username, "password": password}


def get_create_user_input():
    print("\nCreating new user...\n")
    return {
        "username": input("Username: "),
        "password": input("Password: "),
        "first_name": input("First name: "),
        "last_name": input("Last name: "),
        "role": input("Role (manager/employee): "),
    }

def print_error(error):
    print(f"\n-----------------\nError: {error}\n-----------------\n")