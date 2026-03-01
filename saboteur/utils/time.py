import pytz
from datetime import datetime


def get_kst_now_isoformat() -> str:
    """Returns the current time in KST (UTC+9) as an ISO 8601 formatted string."""
    kst_tz = pytz.timezone("Asia/Seoul")
    return datetime.now(kst_tz).isoformat()
