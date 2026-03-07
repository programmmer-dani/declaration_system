# Add input validation


def get_login_input():
    username = input("Username: ")
    password = input("Password: ")
    return {"username": username, "password": password}


def get_user_data():
    print("\nCreating new user...\n")
    return {
        "username": input("Username: "),
        "password": input("Password: "),
        "first_name": input("First name: "),
        "last_name": input("Last name: "),
        "role": input("Role (manager/employee): "),
    }
    
def get_employee_data():
    print("\nCreating new employee...\n")
    
    return {
        "first_name": input("First name: "),
        "last_name": input("Last name: "),
        "birthday": input("Birthday: "),
        "gender": input("Gender: "),
        "street_name": input("Street name: "),
        "house_number": input("House number: "),
        "zip_code": input("Zip code: "),
        "city": input("City: "),
        "email": input("Email: "),
        "mobile_phone": input("Mobile phone: "),
        "id_doc_type": input("ID doc type: "),
        "id_doc_number": input("ID doc number: "),
        "bsn": input("BSN: "),
    }


def print_error(error):
    print(f"\n-----------------\nError: {error}\n-----------------\n")