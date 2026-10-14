import datetime
import uuid

SCHEMA_PATIENTS = {
    'Id': int,
    'BIRTHDATE': datetime.date,
    'FIRST': str,
    'LAST': str,
    'GENDER': str
}

GENDER_VALUES = ['M', 'F']

def is_valid_uuid(uuid_to_test, version=2):
    if isinstance(uuid_to_test, float): # NaN values have these datatype
        return False
    try:
        uuid_obj = uuid.UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return True

def is_valid_date(date):
    try:
        new_date = datetime.datetime(date)
        return True
    except ValueError:
        return False


# test_uuid = "f6359fe4-4340-2820-8b76-593a45f5186c"
# print(is_valid_uuid(test_uuid)
