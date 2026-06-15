from datetime import datetime, timezone, timedelta


tz_vietnam = timezone(timedelta(hours=7))


def get_utc7_now():
    return datetime.now(tz_vietnam).replace(tzinfo=None)