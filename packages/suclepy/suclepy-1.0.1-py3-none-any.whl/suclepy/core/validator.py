# suclepy/core/validator.py

import re
from dateutil.parser import parse

def is_valid_email(email: str) -> bool:
    """
    Check if the email is valid.
    """
    if not isinstance(email, str) or "@" not in email:
        return False
    # Simple regex for basic validation
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email))

def is_numeric(value) -> bool:
    """
    Check if a value is numeric.
    """
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False

def is_valid_date(value) -> bool:
    """
    Check if a value can be parsed as a date.
    """
    try:
        parse(str(value), dayfirst=True)
        return True
    except Exception:
        return False
