import datetime

from infrastructure.database import fetch_unread_suspicious_logs

def log_event(activity_desc, username_enc=None, additional_info=None, is_suspicious=False):
    from domain.security.encryption import encrypt_value
    from infrastructure.database import save_log
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    save_log(
        ts,
        username_enc,
        encrypt_value(activity_desc),
        encrypt_value("1" if is_suspicious else "0"),
        encrypt_value(additional_info) if additional_info else None,
    )

def unread_suspicious_log_count():
    return len(fetch_unread_suspicious_logs())
