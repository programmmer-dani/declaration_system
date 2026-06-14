from time import time

from domain.security.temp_password_updator import update_temp_password
from infrastructure.database import find_user_by_username, username_exists
from domain.security.encryption import decrypt_value, encrypt_value
from domain.security.hashing import hash_password, hash_username, verify_password
from logging_system import log_event
from presentation.helpers import get_login_input
import getpass


def secure_claim_data(session, claim_data):
    secured_claim = {
        "user_id_enc": encrypt_value(str(session["user_id"])),
        "claim_date_enc": encrypt_value(claim_data["claim_date"]),
        "project_number_enc": encrypt_value(claim_data["project_number"]),
        "claim_type_enc": encrypt_value(claim_data["claim_type"]),
        "status_enc": encrypt_value("Pending"),
        "approved_by_user_id_enc": None,
        "salary_batch_enc": None,
    }

    if claim_data["claim_type"] == "Travel":
        secured_claim.update({
            "travel_distance_enc": encrypt_value(claim_data["travel_distance"]),
            "from_zip_enc": encrypt_value(claim_data["from_zip_code"]),
            "from_house_number_enc": encrypt_value(claim_data["from_house_number"]),
            "to_zip_enc": encrypt_value(claim_data["to_zip_code"]),
            "to_house_number_enc": encrypt_value(claim_data["to_house_number"]),
        })

    return secured_claim

def secure_user_data(user_data):
    try:
        secured_user_data = {
            "role_enc": encrypt_value(user_data["role"]),
            "username_enc": encrypt_value(user_data["username"]),
            "username_lookup": hash_username(user_data["username"]),
            "password_hash": hash_password(user_data["password"]),
            "first_name_enc": encrypt_value(user_data["first_name"]),
            "last_name_enc": encrypt_value(user_data["last_name"]),
        }
    except ValueError as e:
        log_event("Error securing basic user data", is_suspicious=True, additional_info=f"Error securing basic user data: {e}")
        raise ValueError(f"Error securing basic user data")
    try:
        if user_data["role"] == "employee":
            secured_user_data.update(secure_employee_data(user_data))
    except ValueError as e:
        log_event("Error securing extra employee data", is_suspicious=True, additional_info=f"Error securing extra employee data: {e}")
        raise ValueError(f"Error securing extra employee data")
    return secured_user_data


def secure_employee_data(employee_data):
    return {
        "birthday_enc": encrypt_value(employee_data["birthday"]),
        "gender_enc": encrypt_value(employee_data["gender"]),
        "street_name_enc": encrypt_value(employee_data["street_name"]),
        "house_number_enc": encrypt_value(employee_data["house_number"]),
        "zip_code_enc": encrypt_value(employee_data["zip_code"]),
        "city_enc": encrypt_value(employee_data["city"]),
        "email_enc": encrypt_value(employee_data["email"]),
        "mobile_phone_enc": encrypt_value(employee_data["mobile_phone"]),
        "id_doc_type_enc": encrypt_value(employee_data["id_doc_type"]),
        "id_doc_number_enc": encrypt_value(employee_data["id_doc_number"]),
        "bsn_enc": encrypt_value(employee_data["bsn"]),
    }

def verify_existing_username(username):
    if username_exists(username):
        raise ValueError("Username already exists")

def login():
    credentials = get_login_input()
    if credentials:
        if credentials["username"] == "super_admin" and credentials["password"] == "Admin_123?":
            log_event("super admin logged in")
            return {"role":"admin", "username_enc": encrypt_value(credentials["username"])}

        user = find_user_by_username(credentials["username"])

        if user is None:
            log_event("failed login attempt", additional_info=f"bad username: {credentials["username"]}")
            return None

        user = dict(user)
        user["role"] = decrypt_value(user["role_enc"])

        is_temp_password = decrypt_value(user["is_password_temp_enc"]) == "1"

        if verify_password(credentials["password"], user["password_hash"]):
            log_event("successful_login", username_enc=encrypt_value(credentials["username"]))
            if is_temp_password:
                update_temp_password(user)
            return user
        else:
            log_event("failed login attempt", additional_info=f"bad password for username: {credentials["username"]}")
            return None
    return None

def reprompt_login(session):
    password = getpass.getpass("Password: ")
    user = find_user_by_username(decrypt_value(session["username_enc"]))
    if verify_password(password, user["password_hash"]):
        log_event("successful_login", username_enc=user["username_enc"])
        return user
    else:
        log_event("failed login attempt", additional_info=f"bad password for username: {decrypt_value(user["username_enc"])}")
        return None
