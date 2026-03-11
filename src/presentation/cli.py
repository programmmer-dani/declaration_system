# Add input validation


def get_login_input():
    username = input("Username: ")
    password = input("Password: ")
    return {"username": username, "password": password}


def get_user_data():
    print("\nCreating new user...\n")
    user_data = {
        "username": input("Username: "),
        "password": input("Password: "),
        "first_name": input("First name: "),
        "last_name": input("Last name: "),
        "role": input("Role (manager/employee): "),
    }
    if user_data["role"] == "employee":
        employee_data = get_employee_data()
        return {**user_data, **employee_data}
    else:
        return user_data
    
def get_employee_data():    
    return {
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
    
def superadmin_menu(): pass
# 1. Login using hardcoded credentials (super_admin / Admin_123?)

# 2. Generate a restore code for a specific manager
#    - create one-time restore code
#    - store hashed restore code in database
#    - associate it with the manager

# 3. Restore database from backup
#    - manager provides restore code
#    - system verifies restore code
#    - restore backup database file

# 4. View restore code status
#    - check if restore code was used or revoked

# 5. Revoke restore code
#    - mark restore code as revoked in database

# 6. Exit system

def manager_menu(): pass
# 1. Create employee account
#    - enter login credentials
#    - enter employee personal data
#    - insert into users table
#    - insert into employees table

# 2. View employee list
#    - show registered employees

# 3. View claims submitted by employees
#    - list claims with status

# 4. Approve claim
#    - set claim status to Approved
#    - set salary_batch

# 5. Reject claim
#    - set claim status to Rejected
#    - set salary_batch

# 6. Generate database backup
#    - create backup of database
#    - store backup file

# 7. Logout

def employee_menu(): pass
# 1. Submit new claim
#    - choose claim type (Travel / Home Office)
#    - enter required claim fields
#    - store claim with status Pending

# 2. View own claims
#    - show claims submitted by employee

# 3. Edit claim
#    - only allowed if salary_batch is NULL
#    - update claim fields

# 4. Delete claim
#    - only allowed if salary_batch is NULL

# 5. Logout