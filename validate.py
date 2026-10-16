import pandas as pd
import numpy as np
import datetime
from prepare_data import load
from utils import is_valid_uuid, is_valid_date

invalidated_patients = []

def make_report(df, df_name, reason_dict):
    report = []
    columns = df.columns

    for reason, invalid_Ids in reason_dict.items():  
        invalid_list = [{'DF': df_name,
                        **{column: df.at[i, column] for column in columns},
                        'Reason': reason} for i in invalid_Ids]
        report.extend(invalid_list)
    return report

def validate_patients(dictionary_df):
    
    # Id cannot be null
    patients = dictionary_df['patients']
    null_Ids = patients[patients['Id'].isna() | patients['Id'].str.strip().eq('')].index

    # Id cannot be duplicated
    duplicate_Ids = patients[patients['Id'].duplicated() == True].index

    # Id must be valid UUID
    invalid_UUIDs_patients = patients['Id'].apply(is_valid_uuid)
    invalid_UUIDs = patients[invalid_UUIDs_patients == False].index

    # Birthdate cannot be null
    null_birthdate_patients = patients['BIRTHDATE'].isna() | patients['BIRTHDATE'].str.strip().eq('')
    null_birthdates = patients[null_birthdate_patients].index

    # Birthdate must be a valid date
    invalid_date_patients = patients['BIRTHDATE'].apply(is_valid_date) 
    invalid_dates_Ids = patients[(invalid_date_patients == False) | (null_birthdate_patients)].index

    # Birthdate must be before TODAY
    today = datetime.date.today()
    birthdates = pd.to_datetime(patients['BIRTHDATE'], errors='coerce').dt.date
    after_today_patients = birthdates > today
    after_today_Ids = patients[after_today_patients == True].index 

    # First name cannot be null
    null_firstname_Ids = patients[patients['FIRST'].isna() | patients['FIRST'].str.strip().eq('')].index

    # Last name cannot be null
    null_lastname_Ids = patients[patients['LAST'].isna() | patients['LAST'].str.strip().eq('')].index
    
    # Gender cannot be null
    null_gender_Ids = patients[patients['GENDER'].isna() |  patients['GENDER'].str.strip().eq('')].index

    # Gender must belong to the allowed set of values (male, female, other)
    allowed = ['M', 'F', 'O']
    not_gender_Ids = patients[
        patients['GENDER'].notna() &
        ~patients['GENDER'].isin(allowed)
    ].index

    # Collection of results and reasons
    reason_dict = {'Id is NaN': null_Ids,
                   'Id is duplicated': duplicate_Ids,
                   'Id is invalid UUID value': invalid_UUIDs,
                   'BIRTHDATE is null': null_birthdates,
                   'BIRTHDATE is invalid': invalid_dates_Ids,
                   'BIRTHDATE is after today': after_today_Ids,
                   'FIRST name is null': null_firstname_Ids,
                   'LAST name is null': null_lastname_Ids,
                   'GENDER is null': null_gender_Ids,
                   'GENDER not in allowed values': not_gender_Ids
                   }
    report_patients = make_report(patients, 'patients', reason_dict=reason_dict)

    print(report_patients)
    return report_patients

def validate_encounters(dictionary_df):
    pass

def validate_observations(dictionary_df):
    pass

def main():
    dictionary_df = load('test_data')

    report_patients = validate_patients(dictionary_df)
    validate_encounters(dictionary_df)
    validate_observations(dictionary_df)

if __name__ == '__main__':
    main()
