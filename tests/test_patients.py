import pandas as pd
import pytest

from validate import validate_patients

@pytest.fixture
def patients_data():
    patients = pd.DataFrame(
        {
            "Id": [
                "65cbad6a-eb9d-420e-9bab-b4f9c6aab7db",  # 0: valid
                None,                                    # 1: null Id
                "7132442e-b0b9-a886-e28d-f83700e5a3bd",  # 2: duplicate
                "not-a-valid-uuid",                      # 3: invalid UUID
                "cc3eac4a-34a7-9a15-13f3-57f4a6b934f9",  # 4: future birthdate
                "8b9df7af-24b3-66ee-d46c-520a00b76fa8",  # 5: null first name
                "65cbad6a-eb9d-420e-0c28-4eb837f969bc",  # 6: null last name
                "65cbad6a-eb9d-420e-0c28-4eb837f969bd",  # 7: null gender
                "65cbad6a-eb9d-420e-0c28-4eb837f969be",  # 8: invalid gender
                "65cbad6a-eb9d-420e-0c28-4eb837f969bf",  # 9: null birthdate
                "65cbad6a-eb9d-420e-0c28-4eb837f969ba",  # 10: invalid birthdate
                "7132442e-b0b9-a886-e28d-f83700e5a3bd",  # 11: duplicate again
                "65cbad6a-eb9d-420e-0c28-4eb837f969bb",  # 12: blank first name
                "65cbad6a-eb9d-420e-0c28-4eb837f969b1",  # 13: blank last name
                "65cbad6a-eb9d-420e-0c28-4eb837f969b2",  # 14: blank gender
            ],
            "BIRTHDATE": [
                "1980-01-01",
                "1990-01-01",
                "1985-06-15",
                "1975-03-20",
                "2999-01-01",
                "1988-12-12",
                "1992-04-03",
                "1970-08-09",
                "1981-02-14",
                None,
                "not-a-date",
                "1985-06-15",
                "1990-01-01",
                "1990-01-01",
                "1990-01-01",
            ],
            "FIRST": [
                "Anna", "Peter", "Maria", "John", "Eva",
                None, "Alex", "Sara", "Tom", "Nina",
                "Mark", "Maria", "   ", "Lukas", "Mia",
            ],
            "LAST": [
                "Test", "Example", "Smith", "Brown", "Green",
                "Jones", None, "White", "Black", "Grey",
                "Stone", "Smith", "Miller", "   ", "Taylor",
            ],
            "GENDER": [
                "F", "M", "F", "M", "F",
                "M", "F", None, "UNKNOWN", "F",
                "M", "F", "F", "M", "   ",
            ],
        }
    )

    return {"patients": patients}

def errors_for(report, index, reason):
    return [
        item for item in report
        if item["Index"] == index and item["Reason"] == reason
    ]

def test_valid_patient_is_not_in_report(patients_data):
    report, _ = validate_patients(patients_data)
    patients_data_df = patients_data['patients']
    valid_Id = patients_data_df.iloc[0]['Id']

    assert len([item for item in report if item['Id'] == valid_Id]) == 0

def test_null_id_is_reported(patients_data):
    report, _ = validate_patients(patients_data)

    errors = errors_for(report, 1, "Id is NaN")

    assert len(errors) == 1


def test_duplicate_id_is_reported(patients_data):
    report, _ = validate_patients(patients_data)

    errors = errors_for(report, 11, "Id is duplicated")

    assert len(errors) == 1


def test_invalid_uuid_is_reported(patients_data):
    report, _ = validate_patients(patients_data)

    errors = errors_for(report, 3, "Id is invalid UUID value")

    assert len(errors) == 1


def test_duplicate_id_is_reported(patients_data):
    report, _ = validate_patients(patients_data)

    errors = errors_for(report, 11, "Id is duplicated")

    assert len(errors) == 1


def test_null_first_name_is_reported(patients_data):
    report, _ = validate_patients(patients_data)

    errors = errors_for(report, 5, "FIRST name is null")

    assert len(errors) == 1


def test_blank_first_name_is_reported(patients_data):
    report, _ = validate_patients(patients_data)

    errors = errors_for(report, 12, "FIRST name is null")

    assert len(errors) == 1


def test_null_last_name_is_reported(patients_data):
    report, _ = validate_patients(patients_data)

    errors = errors_for(report, 6, "LAST name is null")

    assert len(errors) == 1


def test_blank_last_name_is_reported(patients_data):
    report, _ = validate_patients(patients_data)

    errors = errors_for(report, 13, "LAST name is null")

    assert len(errors) == 1


def test_null_gender_is_reported(patients_data):
    report, _ = validate_patients(patients_data)

    errors = errors_for(report, 7, "GENDER is null")

    assert len(errors) == 1


def test_invalid_gender_is_reported(patients_data):
    report, _ = validate_patients(patients_data)

    errors = errors_for(report, 8, "GENDER not in allowed values")

    assert len(errors) == 1

def test_future_birthdate_is_reported(patients_data):
    report, _ = validate_patients(patients_data)
    
    errors = errors_for(report, 4, "BIRTHDATE is after today")
    
    assert len(errors) == 1

def test_invalid_birthdate_is_reported(patients_data):
    report, _ = validate_patients(patients_data)

    errors = errors_for(report, 10, "BIRTHDATE is invalid")

    assert len(errors) == 1


def test_null_birthdate_is_reported(patients_data):
    report, _ = validate_patients(patients_data)
    
    errors = errors_for(report, 9, "BIRTHDATE is null")
    
    assert len(errors) == 1

    

