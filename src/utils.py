from datetime import datetime


def modificate_date_to_str() -> str:
    date = datetime.now()
    date_template = "{day}-{month}-{year}"
    return date_template.format(day=date.day, month=date.month, year=date.year)
