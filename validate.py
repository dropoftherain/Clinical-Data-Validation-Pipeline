import pandas as pd
import datetime
from prepare_data import load, save_data
from utils import is_valid_uuid, is_valid_date, is_valid_datetime, check_datatype
from reporting_utils import make_report, make_dictionary, collect_error_indices, filter_validated_data

def validate_patients(dictionary_df):
    """Validate patient rows; return (failure report, rows that passed)."""
    patients = dictionary_df['patients']

    # Id cannot be null
    null_Ids_patients = patients['Id'].isna() | patients['Id'].str.strip().eq('')
    null_Ids = patients[null_Ids_patients].index

    # Id cannot be duplicated
    duplicate_Ids = patients[patients['Id'].duplicated() == True].index

    # Id must be valid UUID
    invalid_UUIDs_patients = patients['Id'].apply(is_valid_uuid)
    invalid_UUIDs = patients[(invalid_UUIDs_patients == False) & (~null_Ids_patients)].index

    # Birthdate cannot be null
    null_birthdate_patients = patients['BIRTHDATE'].isna() | patients['BIRTHDATE'].str.strip().eq('')
    null_birthdates = patients[null_birthdate_patients].index

    # Birthdate must be a valid date
    invalid_date_patients = patients['BIRTHDATE'].apply(is_valid_date) 
    invalid_dates_Ids = patients[(invalid_date_patients == False) & (~null_birthdate_patients)].index

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
    null_gender_patients = patients['GENDER'].isna() |  patients['GENDER'].str.strip().eq('')
    null_gender_Ids = patients[null_gender_patients].index

    # Gender must belong to the allowed set of values (male, female, other)
    allowed = ['M', 'F', 'O']
    not_gender_Ids = patients[
        ~null_gender_patients &
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

    all_error_indices_patients = collect_error_indices(
                                                        null_Ids,
                                                        duplicate_Ids,
                                                        invalid_UUIDs,
                                                        null_birthdates,
                                                        invalid_dates_Ids,
                                                        after_today_Ids,
                                                        null_firstname_Ids,
                                                        null_lastname_Ids,
                                                        null_gender_Ids,
                                                        not_gender_Ids
                                                        )

    patients_validated = filter_validated_data(patients, all_error_indices_patients)

    return report_patients, patients_validated

def validate_encounters(dictionary_df, patients_validated):
    """Validate encounters, including FK checks against original and validated patients."""
    encounters = dictionary_df['encounters']
    patients = dictionary_df['patients']
    
    # Id cannot be null
    null_Ids_encounters = encounters['Id'].isna() | encounters['Id'].str.strip().eq('')
    null_Ids = encounters[null_Ids_encounters].index

    # Id cannot be duplicated
    duplicate_Ids = encounters[encounters['Id'].duplicated() == True].index

    # Id must be valid UUID
    invalid_UUIDs_encounters = encounters['Id'].apply(is_valid_uuid)
    invalid_UUIDs = encounters[~invalid_UUIDs_encounters & ~null_Ids_encounters].index

    # Patient Id cannot be null
    null_patients = encounters['PATIENT'].isna() | encounters['PATIENT'].str.strip().eq('')
    null_patient_Ids = encounters[null_patients].index

    # Patient Id cannot reference non-existing Id
    valid_patient_Id = list(patients['Id'])
    invalid_patient_Ids = encounters[~encounters['PATIENT'].isin(valid_patient_Id) & ~null_patients].index

    # Start cannot be null
    null_start_encounters = encounters['START'].isna() | encounters['START'].str.strip().eq('')
    null_start_Ids = encounters[null_start_encounters].index

    # Start must be a valid datetime
    invalid_datetime_encounters = encounters['START'].apply(is_valid_datetime)
    invalid_datetime_Ids = encounters[~invalid_datetime_encounters & ~null_start_encounters].index

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

    # Patient Id reference must have passed in the patients validation
    validated_patient_Ids = list(patients_validated['Id'])
    not_validated_patient_Ids = encounters[
                                ~encounters['PATIENT'].isin(validated_patient_Ids) &
                                encounters['PATIENT'].isin(valid_patient_Id) &
                                ~null_patients
                            ].index

    # Collection of results and reasons
    reason_dict_e = {'Id is NaN': null_Ids,
                'Id is duplicated': duplicate_Ids,
                'Id is invalid UUID value': invalid_UUIDs,
                'PATIENT Id is null': null_patient_Ids,
                'PATIENT Id references non-existent Id': invalid_patient_Ids,
                'START datetime is null': null_start_Ids,
                'START datetime is invalid': invalid_datetime_Ids,
                'STOP datetime is invalid': invalid_datetime_stop_Ids,
                'STOP datetime is before START datetime': stop_before_start_Ids,
                'References a PATIENT which was not validated': not_validated_patient_Ids
                }
    report_encounters = make_report(encounters, 'encounters', reason_dict=reason_dict_e)

    all_error_indices_encounters = collect_error_indices(
                                                            null_Ids,
                                                            duplicate_Ids,
                                                            invalid_UUIDs,
                                                            null_patient_Ids,
                                                            invalid_patient_Ids,
                                                            null_start_Ids,
                                                            invalid_datetime_Ids,
                                                            invalid_datetime_stop_Ids,
                                                            stop_before_start_Ids,
                                                            not_validated_patient_Ids
                                                            )

    encounters_validated = filter_validated_data(encounters, all_error_indices_encounters)

    return report_encounters, encounters_validated

def validate_observations(dictionary_df, patients_validated, encounters_validated):
    """Validate observations, including FK checks against patients and encounters."""
    patients = dictionary_df['patients']
    encounters = dictionary_df['encounters']
    observations = dictionary_df['observations']

    # Date cannot be null
    null_date_observations = observations['DATE'].isna() | observations['DATE'].str.strip().eq('')
    null_date_Ids = observations[null_date_observations].index

    # Date must be a valid datetime
    invalid_datetime_observations = observations['DATE'].apply(is_valid_datetime)
    invalid_datetime_Ids = observations[(invalid_datetime_observations == False) & ~null_date_observations].index

    # Patient Id cannot be null
    null_patients = observations['PATIENT'].isna() | observations['PATIENT'].str.strip().eq('')
    null_patient_Ids = observations[null_patients].index

    # Patient Id cannot reference non-existing Id
    valid_patient_Ids = list(patients['Id'])
    invalid_patient_Ids = observations[~observations['PATIENT'].isin(valid_patient_Ids) & ~null_patients].index

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

    # Patient Id reference must have passed in the patients validation
    validated_patient_Ids = list(patients_validated['Id'])
    not_validated_patient_Ids = observations[
                                    ~observations['PATIENT'].isin(validated_patient_Ids) &
                                    observations['PATIENT'].isin(valid_patient_Ids) &
                                    ~null_patients
                                ].index

    # Enounter Id reference must have passed in the encounters validation
    validated_encounter_Ids = list(encounters_validated['Id'])
    not_validated_encounter_Ids = observations[
                                        ~observations['ENCOUNTER'].isin(validated_encounter_Ids) &
                                        observations['ENCOUNTER'].isin(valid_encounter_Ids) &
                                        ~null_encounter_Ids
                                    ].index
    
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
                    'TYPE does not correspond to the datatype of VALUE': not_corr_datatype_Ids,
                    'References a PATIENT which was not validated': not_validated_patient_Ids,
                    'References an ENCOUNTER which was not validated': not_validated_encounter_Ids
                    }
    
    report_observations = make_report(observations, 'observations', reason_dict=reason_dict_o)

    all_error_indices_observations = collect_error_indices(
                                                                null_date_Ids,
                                                                invalid_datetime_Ids,
                                                                null_patient_Ids,
                                                                invalid_patient_Ids,
                                                                invalid_encounter_Ids,
                                                                null_category_Ids,
                                                                invalid_category_Ids,
                                                                null_value_observations,
                                                                null_type_observations,
                                                                not_corr_datatype_Ids,
                                                                not_validated_patient_Ids,
                                                                not_validated_encounter_Ids
                                                                )

    observations_validated = filter_validated_data(observations, all_error_indices_observations)
    
    return report_observations, observations_validated

def main():
    """Run full validation on test_data/ and write reports/ plus validated_data/."""
    dictionary_df = load('test_data')

    report_patients, patients_validated = validate_patients(dictionary_df)
    report_encounters, encounters_validated = validate_encounters(dictionary_df, patients_validated)
    report_observations, observations_validated = validate_observations(dictionary_df, patients_validated, encounters_validated)

    dictionary_reports = make_dictionary(report_patients, report_encounters, report_observations)
    save_data(dictionary_reports, 'reports')

    validated = make_dictionary(patients_validated, encounters_validated, observations_validated)
    save_data(validated, 'validated_data')

if __name__ == '__main__':
    main()
