import pandas as pd
import datetime
from prepare_data import load, save_data
from utils import is_valid_uuid, is_valid_date, is_valid_datetime, check_datatype

def make_report(df, df_name, reason_dict):
    report = []
    columns = df.columns

    for reason, invalid_Ids in reason_dict.items():  
        invalid_list = [{'DF': df_name,
                         'Index': i,
                        **{column: df.at[i, column] for column in columns},
                        'Reason': reason} for i in invalid_Ids]
        report.extend(invalid_list)
    return report

def validate_patients(dictionary_df):

    patients = dictionary_df['patients']

    # Id cannot be null
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

    return report_patients

def validate_encounters(dictionary_df):

    encounters = dictionary_df['encounters']
    patients = dictionary_df['patients']
    
    # Id cannot be null
    null_Ids = encounters[encounters['Id'].isna() | encounters['Id'].str.strip().eq('')].index

    # Id cannot be duplicated
    duplicate_Ids = encounters[encounters['Id'].duplicated() == True].index

    # Id must be valid UUID
    invalid_UUIDs_encounters = encounters['Id'].apply(is_valid_uuid)
    invalid_UUIDs = encounters[invalid_UUIDs_encounters == False].index

    # Patient Id cannot be null
    null_patient_Ids = encounters[encounters['PATIENT'].isna() | encounters['PATIENT'].str.strip().eq('')].index

    # Patient Id cannot reference non-existing Id
    valid_patient_Id = list(patients['Id'])
    invalid_patient_Ids = encounters[~encounters['PATIENT'].isin(valid_patient_Id)].index

    # Start cannot be null
    null_start_encounters = encounters['START'].isna() | encounters['START'].str.strip().eq('')
    null_start_Ids = encounters[null_start_encounters].index

    # Start must be a valid datetime
    invalid_datetime_encounters = encounters['START'].apply(is_valid_datetime)
    invalid_datetime_Ids = encounters[(invalid_datetime_encounters == False) | null_start_encounters].index

    # Stop (if present) must be a valid datetime
    null_stop_mask = encounters['STOP'].isna() | encounters['STOP'].str.strip().eq('') # ALLOWED, but necessary for filter
    invalid_stop_datetime_encounters = encounters['STOP'].apply(is_valid_datetime)
    invalid_datetime_stop_Ids = encounters[(invalid_stop_datetime_encounters == False) & (~null_stop_mask)].index

    # Stop cannot be before start
    starts = pd.to_datetime(encounters['START'], errors='coerce')
    stops = pd.to_datetime(encounters['STOP'], errors='coerce')

    stop_before_start_mask = (
        starts.notna() &
        stops.notna() &
        (stops < starts)
    )
    stop_before_start_Ids = encounters[stop_before_start_mask].index

    # Collection of results and reasons
    reason_dict_e = {'Id is NaN': null_Ids,
                'Id is duplicated': duplicate_Ids,
                'Id is invalid UUID value': invalid_UUIDs,
                'PATIENT Id is null': null_patient_Ids,
                'PATIENT Id references non-existent Id': invalid_patient_Ids,
                'START datetime is null': null_start_Ids,
                'START datetime is invalid': invalid_datetime_Ids,
                'STOP datetime is invalid': invalid_datetime_stop_Ids,
                'STOP datetime is before START datetime': stop_before_start_Ids
                }
    report_encounters = make_report(encounters, 'encounters', reason_dict=reason_dict_e)

    return report_encounters

def validate_observations(dictionary_df):

    patients = dictionary_df['patients']
    encounters = dictionary_df['encounters']
    observations = dictionary_df['observations']

    # Date cannot be null
    null_date_observations = observations['DATE'].isna() | observations['DATE'].str.strip().eq('')
    null_date_Ids = observations[null_date_observations].index

    # Date must be a valid datetime
    invalid_datetime_observations = observations['DATE'].apply(is_valid_datetime)
    invalid_datetime_Ids = observations[(invalid_datetime_observations == False) | null_date_observations].index

    # Patient Id cannot be null
    null_patient_Ids = observations[observations['PATIENT'].isna() | observations['PATIENT'].str.strip().eq('')].index

    # Patient Id cannot reference non-existing Id
    valid_patient_Ids = list(patients['Id'])
    invalid_patient_Ids = observations[~observations['PATIENT'].isin(valid_patient_Ids)].index

    # Encounter Id cannot reference non-existing Id
    null_encounter_Ids = observations['ENCOUNTER'].isna() | observations['ENCOUNTER'].str.strip().eq('') # ALLOWED, just a mask
    valid_encounter_Ids = list(encounters['Id'])
    invalid_encounter_Ids = observations[~observations['ENCOUNTER'].isin(valid_encounter_Ids) & ~null_encounter_Ids].index

    # Category cannot be null
    null_category_observations = observations['CATEGORY'].isna() | observations['CATEGORY'].str.strip().eq('')
    null_category_Ids = observations[null_category_observations].index

    # Category must be in allowed values
    allowed_categories = ['laboratory', 'survey', 'vital-signs', 'social-history', 'exam', 'imaging', 'procedure', 'therapy']
    invalid_category_Ids = observations[~observations['CATEGORY'].isin(allowed_categories) & ~null_category_observations].index

    # Value cannot be null
    value_as_string = observations['VALUE'].astype('string')
    missing_value_mask = (observations["VALUE"].isna() | value_as_string.str.strip().eq("").fillna(False))
    null_value_observations = observations[missing_value_mask].index

    # Type cannot be null
    type_as_string = observations["TYPE"].astype("string")
    missing_type_mask = (observations["TYPE"].isna()| type_as_string.str.strip().eq("").fillna(False))
    null_type_observations = observations[missing_type_mask].index

    # Type has to correspond to the datatype of value
    datatypes = observations['VALUE'].apply(check_datatype)
    not_corr_datatype_Ids = observations[~missing_value_mask & ~missing_type_mask & observations["TYPE"].ne(datatypes)].index

    # Collection of results and reasons
    reason_dict_o = {'DATE is null': null_date_Ids,
                    'DATE datetime is invalid': invalid_datetime_Ids,
                    'PATIENT Id is null': null_patient_Ids,
                    'PATIENT Id references non-existent Id': invalid_patient_Ids,
                    'ENCOUNTER Id references non-existent Id': invalid_encounter_Ids,
                    'CATEGORY is null': null_category_Ids,
                    'CATEGORY is not allowed value': invalid_category_Ids,
                    'VALUE is null': null_value_observations,
                    'TYPE is null': null_type_observations,
                    'TYPE does not correspond to the datatype of VALUE': not_corr_datatype_Ids
                    }
    report_observations = make_report(observations, 'observations', reason_dict=reason_dict_o)

    return report_observations

def main():

    dictionary_df = load('test_data')

    report_patients = validate_patients(dictionary_df)
    report_encounters = validate_encounters(dictionary_df)
    report_observations = validate_observations(dictionary_df)

    dictionary_reports = {
        'patients': pd.DataFrame(report_patients),
        'encounters': pd.DataFrame(report_encounters),
        'observations': pd.DataFrame(report_observations)
    }

    save_data(dictionary_reports, 'reports')

if __name__ == '__main__':
    main()
