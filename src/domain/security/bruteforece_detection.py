import datetime
from domain.security.encryption import decrypt_value
from infrastructure.database import fetch_logs_since_created_at

def is_bruteforce_lockout_active(now=None):
    created_at_fmt = "%Y%m%d_%H%M%S"
    window_seconds = 60
    failure_threshold = 5

    if now is None:
        now = datetime.datetime.now()
    cutoff = now - datetime.timedelta(seconds=window_seconds)
    since = cutoff.strftime(created_at_fmt)

    count = 0
    for row in fetch_logs_since_created_at(since):
        try:
            activity = decrypt_value(row["activity_desc_enc"])
        except Exception:
            continue
        if activity == "failed login attempt":
            count += 1
            if count >= failure_threshold:
                return True
    return False
