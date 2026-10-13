import pandas as pd
import numpy as np
from prepare_data import load
from utils import is_valid_uuid

invalidated_patients = []

def validate_patients(dictionary_df):
    # Id cannot be null
    patients = dictionary_df['patients']
    null_Ids = patients[patients['Id'].isna()].index

    # Id cannot be duplicated
    duplicate_Ids = patients[patients['Id'].duplicated() == True].index

    # Id must be valid UUID
    patients['check_for_valid_UUID'] = patients['Id'].apply(is_valid_uuid)
    invalid_UUIDs = patients[patients['check_for_valid_UUID'] == False].index

    # Collection of results and reasons
    reason_dict = {'Id is NaN': null_Ids, 'Id is duplicated': duplicate_Ids, 'Id is invalid UUID value': invalid_UUIDs}
    for reason, invalid_Ids in reason_dict.items():
        invalid_list = [{"DF": 'patients',
                        'Id': patients.at[i,'Id'],
                        'BIRTHDATE': patients.at[i,'BIRTHDATE'],
                        'FIRST': patients.at[i,'FIRST'],
                        'LAST': patients.at[i, 'LAST'],
                        'GENDER': patients.at[i,'GENDER'],
                        'Reason': reason} for i in invalid_Ids]
        invalidated_patients.extend(invalid_list)

    print(invalidated_patients)

def validate_encounters(dictionary_df):
    pass

def validate_observations(dictionary_df):
    pass

def main():
    dictionary_df = load('test_data')

    validate_patients(dictionary_df)
    validate_encounters(dictionary_df)
    validate_observations(dictionary_df)

if __name__ == '__main__':
    main()
