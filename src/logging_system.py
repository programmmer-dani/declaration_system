import datetime

from domain.security.encryption import encrypt_value
from infrastructure.database import fetch_unread_logs, save_log


def log_activity(username_enc, activity_desc, is_suspicious, additional_info=None):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    activity_desc_enc = encrypt_value(activity_desc)
    if additional_info:
        additional_info_enc = encrypt_value(additional_info)
    else:
        additional_info_enc = None
    save_log(ts, username_enc, activity_desc_enc, is_suspicious, additional_info_enc) # should ts get encrypted?
    
def uread_log_count():
    return len(fetch_unread_logs())