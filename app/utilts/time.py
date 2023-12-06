from datetime import datetime

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

def format_datetime(dt: datetime) -> str:
    return dt.strftime(TIME_FORMAT)

def parse_daetetime(dt: str) -> datetime:
    return datetime.strptime(dt, TIME_FORMAT)

def current_datetime_str() -> str:
    return format_datetime(datetime.now())