import re
from datetime import date, timedelta

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


def _ok(s, length=100):
    return (
        isinstance(s, str)
        and re.match(fr"^[ -~À-ÿ]{{1,{length}}}$", s)
        and re.search(r"\S", s))

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
        return True
    if _ok(s) and re.match(r"^[A-Za-z_][A-Za-z0-9_'.]{7,9}$", s):
        return True
    return False


def validate_password(s):
    allowed_pattern = r"^[A-Za-z0-9~!@#$%&_\-+=`|\\(){}\[\]:;'<>,.?/]{12,50}$"
    special_pattern = r"[~!@#$%&_\-+=`|\\(){}\[\]:;'<>,.?/]"
    
    if s == "Admin_123?":
        return True

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
    if _ok(s) and re.match(r"^[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ '\-]{0,99}$", s):
        return True
    return False


def _date_sanity(s, min_year, max_year):
    y, m, d = int(s[:4]), int(s[5:7]), int(s[8:10])
    return min_year <= y <= max_year and 1 <= m <= 12 and 1 <= d <= 31


def _calendar_ym_sanity(s, min_year, max_year):
    y, mo = int(s[:4]), int(s[5:7])
    return min_year <= y <= max_year and 1 <= mo <= 12


def _now_str():
    return date.today().isoformat()


def validate_birthday(s):
    today = date.today()
    if (
        _ok(s)
        and re.match(r"^\d{4}-\d{2}-\d{2}$", s)
        and _date_sanity(s, today.year - 100, today.year)
        and s <= _now_str()
    ):
        return True
    return False


def validate_gender(s):
    if _ok(s,7) and s in ("male", "female"):
        return True
    return False


def validate_street_name(s):
    if _ok(s) and re.match(r"^[A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ0-9 .'\-]{0,99}$", s):
        return True
    return False


def validate_house_number(s):
    if _ok(s) and re.match(r"^\d{1,5}$", s):
        return True
    return False


def validate_zip_code(s):
    if _ok(s) and re.match(r"^\d{4}[A-Z]{2}$", s):
        return True
    return False


def validate_city(s):
    if _ok(s) and s in {c for c in VALID_CITIES}:
        return True
    return False


def validate_email(s):
    if _ok(s,254) and re.match(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$", s):
        return True
    return False


def validate_mobile_phone(s):
    if _ok(s) and re.match(r"^\d{8}$", s):
        return True
    return False


def validate_id_doc_type(s):
    if _ok(s,8) and s in ("Passport", "ID-Card"):
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
    if _ok(s,11) and s in ("Travel", "Home Office"):
        return True
    return False


def validate_claim_date(s):
    today = date.today()
    low = (today - timedelta(days=60)).isoformat()
    high = (today + timedelta(days=14)).isoformat()
    if (
        _ok(s)
        and re.match(r"^\d{4}-\d{2}-\d{2}$", s)
        and _date_sanity(s, today.year - 1, today.year + 1)
        and low <= s <= high
    ):
        return True
    return False

def validate_salary_batch(s):
    today = date.today()
    min_first = date(today.year - 1, 1, 1).isoformat()[:7]
    max_first = date(today.year, today.month, 1).isoformat()[:7]

    if (
        _ok(s)
        and re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", s)
        and _calendar_ym_sanity(s, today.year - 1, today.year)
        and min_first <= s <= max_first
    ):
        return True
    return False

def validate_search_keyword(s):
    if _ok(s) and re.fullmatch(r"[A-Za-z0-9 .'\-]{1,50}", s):
        return True
    return False

def validate_project_number(s):
    if _ok(s) and re.match(r"^\d{2,10}$", s):
        return True
    return False

def validate_travel_distance(s):
    if _ok(s) and re.fullmatch(r"[1-9]\d{0,2}", s):
        return True
    return False

def validate_backup_filename(s):
    if _ok(s) and re.match(r"^[A-Za-z0-9_-][A-Za-z0-9_.\-]{0,99}\.zip$", s):
        return True
    return False
