from datetime import datetime, date

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATE_FORMAT = '%Y-%m-%d'


def format_datetime(dt: datetime) -> str:
    return dt.strftime(TIME_FORMAT)


def parse_datetime(dt: str) -> datetime:
    return datetime.strptime(dt, TIME_FORMAT)


def format_date(dt: datetime | date) -> str:
    return dt.strftime(DATE_FORMAT)


def parse_date(dt: str) -> datetime:
    return datetime.strptime(dt, DATE_FORMAT)


def current_datetime_str() -> str:
    return format_datetime(datetime.now())
