import datetime
import pandas as pd
import uuid

def is_valid_uuid(uuid_to_test, version=2):
    """Return True if value is a parseable UUID string."""
    if not isinstance(uuid_to_test, str) or not uuid_to_test.strip():
        return False
    try:
        uuid_obj = uuid.UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return True

def is_valid_date(date):
    """Validate a date in YYYY-MM-DD format."""
    if pd.isna(date) or not isinstance(date, str):
        return False
    try:
        new_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return False
    return True

def is_valid_datetime(datetime_x):
    """Validate an ISO-style datetime with a timezone."""
    if pd.isna(datetime_x):
        return False
    try:
        datetime.datetime.strptime(str(datetime_x), "%Y-%m-%dT%H:%M:%S%z")
        return True
    except ValueError:
        return False

def check_datatype(value):
    """Classify a value as numeric, text, or missing."""
    if pd.isna(value):
        return "missing"
    try:
        float(value)
        return 'numeric'
    except ValueError:
        return 'text'

# print(is_valid_datetime("1996-03-32T09:21:33Z"))
# print(check_datatype('80'))       # numeric
# print(check_datatype('6.3'))      # numeric
# print(check_datatype('eighty'))   # text