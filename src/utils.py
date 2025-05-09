import re
from datetime import datetime


def modificate_date_to_str() -> str:
    date = datetime.now()
    date_template = "{day}-{month}-{year}"
    return date_template.format(day=date.day, month=date.month, year=date.year)


def validate_date(date: str) -> bool:
    re_template = r"^(\d{1,2})-(\d{1,2})-(\d{4})$"
    match = re.fullmatch(re_template, date)

    if match:
        return True
    else:
        return False
