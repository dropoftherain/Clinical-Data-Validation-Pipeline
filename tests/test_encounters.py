import pandas as pd
import pytest

from validate import validate_encounters


@pytest.fixture
def encounters_data():
    encounters = pd.DataFrame(
        {
            "Id": [
                "11111111-1111-4111-8111-111111111111",  # 0: valid
                "22222222-2222-4222-8222-222222222222",  # 1: missing START
                "33333333-3333-4333-8333-333333333333",  # 2: invalid patient
                "44444444-4444-4444-8444-444444444444",  # 3: START after STOP
                "not-a-valid-uuid",                      # 4: invalid UUID
                "11111111-1111-4111-8111-111111111111",  # 5: duplicate ID
                "66666666-6666-4666-8666-666666666666",  # 6: invalid START
                "77777777-7777-4777-8777-777777777777",  # 7: missing PATIENT, missing STOP
                None,                                    # 8: null Id 
                "88888888-8888-4888-8888-888888888888",  # 9: Patient Id not in validated patients
            ],

            "PATIENT": [
                "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
                "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
                "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
                "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
                "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
                "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
                "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
                None,
                "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
                "cccccccc-cccc-4ccc-8ccc-cccccccccccc"  # Assuming that it is not present in validated patients
            ],
            "START": [
                "2024-01-10T10:00:00Z",
                None,
                "2024-02-10T10:00:00Z",
                "2024-03-10T12:00:00Z",
                "2024-04-10T10:00:00Z",
                "2024-05-10T10:00:00Z",
                "not-a-datetime",
                "2024-07-10T10:00:00Z",
                "2024-08-10T10:00:00Z",
                "2024-09-10T10:00:00Z",
            ],
            "STOP": [
                "2024-01-10T11:00:00Z",
                "2024-01-11T11:00:00Z",
                "2024-02-10T11:00:00Z",
                "2024-03-10T11:00:00Z",
                "2024-04-10T11:00:00Z",
                "2024-05-10T11:00:00Z",
                "2024-06-10T11:00:00Z",
                "not-a-datetime",
                "2024-08-10T12:00:00Z",
                "2024-09-10T12:00:00Z",
            ],
            "ENCOUNTERCLASS": [
                "ambulatory",
                "ambulatory",
                "outpatient",
                "wellness",
                "ambulatory",
                "ambulatory",
                "outpatient",
                "wellness",
                "ambulatory",
                "ambulatory",
            ],
            "DESCRIPTION": [
                "Valid encounter",
                "Missing start",
                "Unknown patient",
                "Start after stop",
                "Invalid UUID",
                "Duplicate ID",
                "Invalid start",
                "Missing patient and missing stop",
                "Null Id",
                "References a PATIENT which was not validated"
            ],
            "REASONCODE": [
                None, None, None, None, None, None, None, None, None, None
            ],
            "REASONDESCRIPTION": [
                None, None, None, None, None, None, None, None, None, None
            ],
        }
    )

    patients = pd.DataFrame(
        {
            "Id": [
                "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
                "cccccccc-cccc-4ccc-8ccc-cccccccccccc"
            ]
        }
    )

    validated_patients = pd.DataFrame(
        {
            "Id": [
                            "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
                            "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"    
                        ],
        }
    )

    return {
        "patients": patients,
        "encounters": encounters,
        "validated_patients": validated_patients
    }


def errors_for(report, index, reason):
    return [
        item for item in report
        if item["Index"] == index and item["Reason"] == reason
    ]


def test_valid_encounter_is_not_in_report(encounters_data):
    report, _ = validate_encounters(encounters_data, encounters_data["validated_patients"])

    errors = [
        item for item in report
        if item["Index"] == 0
    ]

    assert len(errors) == 0


def test_invalid_uuid_is_reported(encounters_data):
    report, _ = validate_encounters(encounters_data, encounters_data["validated_patients"])

    errors = errors_for(
        report, 4, "Id is invalid UUID value"
    )

    assert len(errors) == 1

def test_null_id_is_reported(encounters_data):
    report, _ = validate_encounters(encounters_data, encounters_data["validated_patients"])

    errors = errors_for(
        report, 8, "Id is NaN"
    )

    assert len(errors) == 1


def test_duplicate_id_is_reported(encounters_data):
    report, _ = validate_encounters(encounters_data, encounters_data["validated_patients"])

    errors = errors_for(
        report, 5, "Id is duplicated"
    )

    assert len(errors) == 1


def test_nonexistent_patient_is_reported(encounters_data):
    report, _ = validate_encounters(encounters_data, encounters_data["validated_patients"])

    errors = errors_for(
        report, 2, "PATIENT Id references non-existent Id"
    )

    assert len(errors) == 1


def test_null_patient_is_reported(encounters_data):
    report, _ = validate_encounters(encounters_data, encounters_data["validated_patients"])

    errors = errors_for(
        report, 7, "PATIENT Id is null"
    )

    assert len(errors) == 1

def test_null_start_is_reported(encounters_data):
    report, _ = validate_encounters(encounters_data, encounters_data["validated_patients"])

    errors = errors_for(
        report, 1, "START datetime is null"
    )

    assert len(errors) == 1


def test_invalid_start_datetime_is_reported(encounters_data):
    report, _ = validate_encounters(encounters_data, encounters_data["validated_patients"])

    errors = errors_for(
        report, 6, "START datetime is invalid"
    )

    assert len(errors) == 1

def test_invalid_stop_datetime_is_reported(encounters_data):
    report, _ = validate_encounters(encounters_data, encounters_data["validated_patients"])

    errors = errors_for(
        report, 7, "STOP datetime is invalid"
    )

    assert len(errors) == 1


def test_start_after_stop_is_reported(encounters_data):
    report, _ = validate_encounters(encounters_data, encounters_data["validated_patients"])

    errors = errors_for(
        report, 3, "STOP datetime is before START datetime"
    )

    assert len(errors) == 1

def test_validated_patient_not_reported(encounters_data):
    report, _ = validate_encounters(encounters_data, encounters_data["validated_patients"])

    errors = [
        item for item in report
        if item["Index"] == 0
    ]

    assert len(errors) == 0

def test_invalidated_patient_reported(encounters_data):
    report, _ = validate_encounters(encounters_data, encounters_data["validated_patients"])
    
    errors = errors_for(
            report, 9, "References a PATIENT which was not validated"
        )

    assert len(errors) == 1


def test_nonvalidated_patient_references_are_filtered_out(encounters_data):
    _, encounters_validated = validate_encounters(
        encounters_data,
        encounters_data["validated_patients"]
    )

    assert 9 not in encounters_validated.index


def test_valid_encounter_remains_in_validated_data(encounters_data):
    _, encounters_validated = validate_encounters(
        encounters_data,
        encounters_data["validated_patients"]
    )

    assert 0 in encounters_validated.index