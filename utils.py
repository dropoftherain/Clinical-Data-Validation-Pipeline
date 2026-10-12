import datetime

SCHEMA_PATIENTS = {
    'Id': int,
    'BIRTHDATE': datetime.date,
    'FIRST': str,
    'LAST': str,
    'GENDER': str
}

GENDER_VALUES = ['M', 'F']