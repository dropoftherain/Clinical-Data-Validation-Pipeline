import datetime
import pandas as pd
import uuid

SCHEMA_PATIENTS = {
    'Id': int,
    'BIRTHDATE': datetime.date,
    'FIRST': str,
    'LAST': str,
    'GENDER': str
}

GENDER_VALUES = ['M', 'F', 'O']

def is_valid_uuid(uuid_to_test, version=2):
    if isinstance(uuid_to_test, float): # NaN values have these datatype
        return False
    try:
        uuid_obj = uuid.UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return True

def is_valid_date(date):
    if pd.isna(date) is None:
        return False
    try:
        new_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return False
    return True

def is_valid_datetime(datetime_x):
    if pd.isna(datetime_x):
        return False
    try:
        datetime.datetime.strptime(str(datetime_x), "%Y-%m-%dT%H:%M:%S%z")
        return True
    except ValueError:
        return False

def check_datatype(value):
    try:
        float(value)
        return 'numeric'
    except ValueError:
        return 'text'

print(is_valid_datetime("1996-03-32T09:21:33Z"))
print(check_datatype('80'))       # numeric
print(check_datatype('6.3'))      # numeric
print(check_datatype('eighty'))   # text