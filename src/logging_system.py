import datetime

from infrastructure.database import fetch_unread_logs

def log_event(activity_desc, username_enc=None, additional_info=None, is_suspicious=False):
    from domain.security.encryption import encrypt_value
    from infrastructure.database import save_log
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    save_log(
        ts,
        username_enc,
        encrypt_value(activity_desc),
        1 if is_suspicious else 0,
        encrypt_value(additional_info) if additional_info else None,
    )

# def bruteforce_detected():
#     fmt = "%Y%m%d_%H%M%S"
#     wrong = "Incorrect login attempt"
#     bad = []
#     for row in fetch_bad_login_logs():
#         try:
#             if decrypt_value(row["activity_desc_enc"]) == wrong:
#                 bad.append(row)
#         except Exception:
#             continue
#         if len(bad) >= 5:
#             break
#     if len(bad) < 5:
#         return False
#     t_newest = datetime.datetime.strptime(bad[0]["created_at"], fmt)
#     t_oldest = datetime.datetime.strptime(bad[4]["created_at"], fmt)
#     return (t_newest - t_oldest).total_seconds() <= 300

def uread_log_count():
    return len(fetch_unread_logs())
