import re
from datetime import date, datetime, timedelta

VALID_CITIES = {
    "Rotterdam",
    "Amsterdam",
    "Utrecht",
    "The Hague",
    "Eindhoven",
    "Groningen",
    "Tilburg",
    "Breda",
    "Leiden",
    "Delft",
}


def _ok(s):
    return isinstance(s, str) and re.match(r"^[ -~À-ÿ]+$", s) is not None and len(s.strip()) > 0


def validate_menu_choice(s, number_of_choices):
    if (
        isinstance(number_of_choices, int)
        and number_of_choices >= 1
        and _ok(s)
        and re.match(r"^\d{1,2}$", s)
        and 1 <= int(s) <= number_of_choices
    ):
        return True
    return False


def validate_restore_code(s):
    if _ok(s) and re.match(r"^[A-Za-z0-9_\-]{22}$", s):
        return True
    return False


def validate_username(s):
    if s == "super_admin":
        return True # ASSIGNMENT REQUIREMENT HARDCODED EXCEPTION
    if _ok(s) and " " not in s and re.match(r"^[A-Za-z_][A-Za-z0-9_'.]{7,9}$", s): # blacklisting by: and " " not in s fix this
        return True
    return False


def validate_password(s):
    allowed_pattern = r"^[A-Za-z0-9~!@#$%&_\-+=`|\\(){}\[\]:;'<>,.?/]{12,50}$"
    special_pattern = r"[~!@#$%&_\-+=`|\\(){}$begin:math:display$$end:math:display$:;'<>,.?/]"
    
    if s == "Admin_123?":
        return True # ASSIGNMENT REQUIREMENT HARDCODED EXCEPTION

    if (
        _ok(s)
        and re.match(allowed_pattern, s)
        and re.search(r"[a-z]", s)
        and re.search(r"[A-Z]", s)
        and re.search(r"\d", s)
        and re.search(special_pattern, s)
    ):
        return True
    return False


def validate_name(s):
    if _ok(s) and len(s) <= 100 and re.match(r"^[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ '\-]{0,99}$", s):
        return True
    return False


def validate_role(s):
    if _ok(s) and s in ("manager", "employee"):
        return True
    return False


def _valid_calendar_ymd(s):
    if not _ok(s):
        return False
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return True
    except Exception:
        return False


def validate_birthday(s):
    today_str = date.today().isoformat()
    if (
        _ok(s)
        and re.match(r"^\d{4}-\d{2}-\d{2}$", s)
        and _valid_calendar_ymd(s)
        and s <= today_str
    ):
        return True
    return False


def validate_gender(s):
    if isinstance(s, str) and s in ("male", "female"):
        return True
    return False


def validate_street_name(s):
    if _ok(s) and len(s) <= 100 and re.match(r"^[A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ0-9 .'\-]{0,99}$", s):
        return True
    return False


def validate_house_number(s):
    if _ok(s) and re.match(r"^\d{1,10}$", s):
        return True
    return False


def validate_zip_code(s):
    if _ok(s) and re.match(r"^\d{4}[A-Z]{2}$", s.replace(" ", "").upper()): # check if this is allowed and not a vuln.
        return True
    return False


def validate_city(s):
    if _ok(s) and s.strip().lower() in {c.lower() for c in VALID_CITIES}:
        return True
    return False


def validate_email(s):
    if (
        _ok(s)
        and len(s) <= 254
        and re.match(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$", s)
    ):
        return True
    return False


def validate_mobile_phone(s):
    if _ok(s) and re.match(r"^\d{8}$", s):
        return True
    return False


def validate_id_doc_type(s):
    if isinstance(s, str) and s in ("Passport", "ID-Card"):
        return True
    return False


def validate_id_doc_number(s):
    if _ok(s) and (re.match(r"^[A-Z]{2}\d{7}$", s) or re.match(r"^[A-Z]\d{8}$", s)):
        return True
    return False


def validate_bsn(s):
    if _ok(s) and re.match(r"^\d{9}$", s):
        return True
    return False


def validate_claim_type(s):
    if isinstance(s, str) and s in ("Travel", "Home Office"):
        return True
    return False


def validate_claim_date(s):
    today = date.today()
    low = (today - timedelta(days=60)).isoformat()
    high = (today + timedelta(days=14)).isoformat()
    if (
        _ok(s)
        and re.match(r"^\d{4}-\d{2}-\d{2}$", s)
        and _valid_calendar_ymd(s)
        and low <= s <= high
    ):
        return True
    return False


def validate_project_number(s):
    if _ok(s) and re.match(r"^\d{2,10}$", s):
        return True
    return False


def validate_travel_distance(s):
    if _ok(s) and re.match(r"^\d+$", s):
        return True
    return False


def validate_salary_batch(s):
    if _ok(s) and re.match(r"^\d{4}-(0[1-9]|1[0-2])$", s):
        return True
    return False


def validate_restore_code(s):
    if _ok(s) and 12 <= len(s) <= 32 and re.match(r"^[A-Za-z0-9]{12,32}$", s):
        return True
    return False


def validate_backup_filename(s):
    if _ok(s) and re.match(r"^[A-Za-z0-9_-][A-Za-z0-9_.\-]{0,99}\.zip$", s):
        return True
    return False
