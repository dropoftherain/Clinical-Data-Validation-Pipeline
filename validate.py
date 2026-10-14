import pandas as pd
import numpy as np
from prepare_data import load
from utils import is_valid_uuid

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
    null_Ids = patients[patients['Id'].isna()].index

    # Id cannot be duplicated
    duplicate_Ids = patients[patients['Id'].duplicated() == True].index

    # Id must be valid UUID
    invalid_UUIDs_patients = patients['Id'].apply(is_valid_uuid)
    invalid_UUIDs = patients[invalid_UUIDs_patients == False].index

    # Birthdate cannot be null
    null_birthdate = patients[patients['BIRTHDATE'].isna()].index

    # Birthdate must be a valid date
    # To be continued
        

    # Collection of results and reasons
    reason_dict = {'Id is NaN': null_Ids,
                   'Id is duplicated': duplicate_Ids,
                   'Id is invalid UUID value': invalid_UUIDs,
                   'BIRTHDATE is null': null_birthdate}
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
