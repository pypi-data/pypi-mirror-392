from datetime import datetime

def to_dd_mm_yyyy(date: datetime) -> str:
    return date.strftime("%d-%m-%Y")

def to_slash_format(date: datetime) -> str:
    return date.strftime("%d/%m/%Y")

def to_full_indian_format(date: datetime) -> str:
    return date.strftime("%d %B %Y")

def to_short_month_format(date: datetime) -> str:
    return date.strftime("%d-%b-%Y")

