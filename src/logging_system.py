import datetime

from domain.security.encryption import decrypt_value, encrypt_value
from infrastructure.database import fetch_last2_logs, fetch_unread_logs, save_log

### IMPLEMENT THIS CODE FOR LOGGING IN
def log_event(activity_desc, is_suspicious=False, username_enc=None, additional_info=None):
    fmt = "%Y%m%d_%H%M%S"
    now = datetime.datetime.now()
    last2 = fetch_last2_logs()
    wrong = "Incorrect login attempt"
    if (
        len(last2) >= 2
        and activity_desc == wrong
        and decrypt_value(last2[0]["activity_desc_enc"]) == wrong
        and decrypt_value(last2[1]["activity_desc_enc"]) == wrong
    ):
        t1 = datetime.datetime.strptime(last2[0]["created_at"], fmt)
        t0 = datetime.datetime.strptime(last2[1]["created_at"], fmt)
        if (t1 - t0).total_seconds() <= 120 and (now - t0).total_seconds() <= 120:
            is_suspicious = True

    ts = now.strftime(fmt)
    activity_desc_enc = encrypt_value(activity_desc)
    additional_info_enc = encrypt_value(additional_info) if additional_info else None
    save_log(ts, username_enc, activity_desc_enc, is_suspicious, additional_info_enc)


def uread_log_count():
    return len(fetch_unread_logs())
