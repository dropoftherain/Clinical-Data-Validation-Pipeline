
import pandas as pd
import pytest

from validate import validate_observations


@pytest.fixture
def observations_data():
    patients = pd.DataFrame({
        "Id": [
            "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            "cccccccc-cccc-4ccc-8ccc-cccccccccccc",
        ]
    })

    encounters = pd.DataFrame({
        "Id": [
            "11111111-1111-4111-8111-111111111111",
            "33333333-3333-4333-8333-333333333333",
        ]
    })

    validated_patients = pd.DataFrame({
        "Id": [
            "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
        ]
    })

    validated_encounters = pd.DataFrame({
        "Id": [
            "11111111-1111-4111-8111-111111111111",
        ]
    })

    observations = pd.DataFrame({
        "DATE": [
            "2024-01-10T10:00:00Z",  # 0: valid
            None,                    # 1: missing DATE
            "not-a-datetime",        # 2: invalid DATE
            "2024-01-10T10:00:00Z",  # 3: missing PATIENT
            "2024-01-10T10:00:00Z",  # 4: unknown PATIENT
            "2024-01-10T10:00:00Z",  # 5: unknown ENCOUNTER
            "2024-01-10T10:00:00Z",  # 6: missing CATEGORY
            "2024-01-10T10:00:00Z",  # 7: invalid CATEGORY
            "2024-01-10T10:00:00Z",  # 8: missing VALUE
            "2024-01-10T10:00:00Z",  # 9: missing TYPE
            "2024-01-10T10:00:00Z",  # 10: datatype mismatch
            "2024-01-10T10:00:00Z",  # 11: unvalidated patient
            "2024-01-10T10:00:00Z",  # 12: unvalidated encounter
            "2024-01-10T10:00:00Z"  # 13: both issues
        ],
        "PATIENT": [
            "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            None,
            "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
            "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            "cccccccc-cccc-4ccc-8ccc-cccccccccccc",  # 11
            "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",  # 12
            "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"  # 13
        ],
        "ENCOUNTER": [
            "11111111-1111-4111-8111-111111111111",
            "11111111-1111-4111-8111-111111111111",
            "11111111-1111-4111-8111-111111111111",
            "11111111-1111-4111-8111-111111111111",
            "11111111-1111-4111-8111-111111111111",
            "22222222-2222-4222-8222-222222222222",
            "11111111-1111-4111-8111-111111111111",
            "11111111-1111-4111-8111-111111111111",
            "11111111-1111-4111-8111-111111111111",
            "11111111-1111-4111-8111-111111111111",
            "11111111-1111-4111-8111-111111111111",
            "11111111-1111-4111-8111-111111111111",  # 11
            "33333333-3333-4333-8333-333333333333",  # 12
            "33333333-3333-4333-8333-333333333333"  # 13
        ],
        "CATEGORY": [
            "laboratory",
            "laboratory",
            "laboratory",
            "laboratory",
            "laboratory",
            "laboratory",
            None,
            "unknown-category",
            "laboratory",
            "laboratory",
            "laboratory",
            "laboratory",
            "laboratory",
            "laboratory"
        ],
        "VALUE": [
            "positive",
            "positive",
            "positive",
            "positive",
            "positive",
            "positive",
            "positive",
            "positive",
            None,
            "positive",
            120,
            "positive",
            "positive",
            "positive"
        ],
        "TYPE": [
            "text",
            "text",
            "text",
            "text",
            "text",
            "text",
            "text",
            "text",
            "text",
            None,
            "text",
            "text",
            "text",
            "text"
        ],
    })

    return {
        "patients": patients,
        "encounters": encounters,
        "observations": observations,
        "validated_patients": validated_patients,
        "validated_encounters": validated_encounters,
    }


def errors_for(report, index, reason):
    return [
        item for item in report
        if item["Index"] == index
        and item["Reason"] == reason
    ]

def get_report(observations_data):
    report, _ = validate_observations(
        observations_data,
        observations_data["validated_patients"],
        observations_data["validated_encounters"]
    )
    return report

def test_valid_observation_is_not_in_report(observations_data):
    report = get_report(observations_data)

    errors = [
        item for item in report
        if item["Index"] == 0
    ]

    assert len(errors) == 0


def test_null_date_is_reported(observations_data):
    report = get_report(observations_data)

    errors = errors_for(report, 1, "DATE is null")

    assert len(errors) == 1


def test_invalid_date_is_reported(observations_data):
    report = get_report(observations_data)

    errors = errors_for(
        report, 2, "DATE datetime is invalid"
    )

    assert len(errors) == 1


def test_null_patient_is_reported(observations_data):
    report = get_report(observations_data)

    errors = errors_for(
        report, 3, "PATIENT Id is null"
    )

    assert len(errors) == 1


def test_nonexistent_patient_is_reported(observations_data):
    report = get_report(observations_data)

    errors = errors_for(
        report, 4, "PATIENT Id references non-existent Id"
    )

    assert len(errors) == 1


def test_nonexistent_encounter_is_reported(observations_data):
    report = get_report(observations_data)

    errors = errors_for(
        report, 5, "ENCOUNTER Id references non-existent Id"
    )

    assert len(errors) == 1


def test_null_category_is_reported(observations_data):
    report = get_report(observations_data)

    errors = errors_for(
        report, 6, "CATEGORY is null"
    )

    assert len(errors) == 1


def test_invalid_category_is_reported(observations_data):
    report = get_report(observations_data)

    errors = errors_for(
        report, 7, "CATEGORY is not allowed value"
    )

    assert len(errors) == 1


def test_null_value_is_reported(observations_data):
    report = get_report(observations_data)

    errors = errors_for(
        report, 8, "VALUE is null"
    )

    assert len(errors) == 1


def test_null_type_is_reported(observations_data):
    report = get_report(observations_data)

    errors = errors_for(
        report, 9, "TYPE is null"
    )

    assert len(errors) == 1


def test_mismatched_datatype_is_reported(observations_data):
    report = get_report(observations_data)

    errors = errors_for(
        report, 10,
        "TYPE does not correspond to the datatype of VALUE"
    )

    assert len(errors) == 1


def test_nonvalidated_patient_is_reported(observations_data):
    report = get_report(observations_data)

    errors = errors_for(
        report, 11, "References a PATIENT which was not validated"
    )

    assert len(errors) == 1


def test_nonvalidated_encounter_is_reported(observations_data):
    report = get_report(observations_data)

    errors = errors_for(
        report, 12, "References an ENCOUNTER which was not validated"
    )

    assert len(errors) == 1


def test_observation_with_both_reference_issues_is_reported(observations_data):
    report = get_report(observations_data)

    patient_errors = errors_for(
        report, 13, "PATIENT Id references non-existent Id"
    )

    encounter_errors = errors_for(
        report, 13, "References an ENCOUNTER which was not validated"
    )

    assert len(patient_errors) == 1
    assert len(encounter_errors) == 1


def test_validated_patient_and_encounter_are_not_reported(observations_data):
    report = get_report(observations_data)

    errors = [
        item for item in report
        if item["Index"] == 0
    ]

    assert len(errors) == 0