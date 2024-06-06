import datetime

now_utc = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)
file_creation_datetime = now_utc.strftime("%Y%m%d")


def date_and_time_format():
    return now_utc.strftime("%Y-%m-%d %H:%M:%S")
