import pandas as pd
import pytest

from reporting_utils import (
    make_report,
    make_dictionary,
    collect_error_indices,
    filter_validated_data
)

@pytest.fixture
def sample_patients():
    return pd.DataFrame({
        "Id": [
            "patient_1",
            "patient_2",
            "patient_3",
            "patient_4"
        ],
        "FIRST": [
            "Anna",
            "Peter",
            None,
            "Maria"
        ],
        "GENDER": [
            "F",
            "M",
            "F",
            "F"
        ]
    })


@pytest.fixture
def sample_encounters():
    return pd.DataFrame({
        "Id": [
            "encounter_1",
            "encounter_2"
        ],
        "PATIENT": [
            "patient_1",
            "patient_2"
        ]
    })


@pytest.fixture
def sample_observations():
    return pd.DataFrame({
        "Id": [
            "observation_1",
            "observation_2"
        ],
        "VALUE": [
            120,
            80
        ]
    })


def test_make_report_creates_correct_report(sample_patients):
    reason_dict = {
        "FIRST is null": [2],
        "Id is duplicated": [3]
    }

    report = make_report(
        sample_patients,
        "patients",
        reason_dict
    )

    assert len(report) == 2

    assert report[0]["DF"] == "patients"
    assert report[0]["Index"] == 2
    assert pd.isna(report[0]["FIRST"])
    assert report[0]["Reason"] == "FIRST is null"

    assert report[1]["DF"] == "patients"
    assert report[1]["Index"] == 3
    assert report[1]["Id"] == "patient_4"
    assert report[1]["Reason"] == "Id is duplicated"


def test_make_report_returns_empty_list_when_no_errors(sample_patients):
    report = make_report(
        sample_patients,
        "patients",
        {}
    )

    assert report == []



def test_make_dictionary_creates_correct_dictionary(
    sample_patients,
    sample_encounters,
    sample_observations
):
    dictionary = make_dictionary(
        sample_patients,
        sample_encounters,
        sample_observations
    )

    assert list(dictionary.keys()) == [
        "patients",
        "encounters",
        "observations"
    ]

    assert isinstance(dictionary["patients"], pd.DataFrame)
    assert isinstance(dictionary["encounters"], pd.DataFrame)
    assert isinstance(dictionary["observations"], pd.DataFrame)

    pd.testing.assert_frame_equal(
        dictionary["patients"],
        sample_patients
    )

    pd.testing.assert_frame_equal(
        dictionary["encounters"],
        sample_encounters
    )

    pd.testing.assert_frame_equal(
        dictionary["observations"],
        sample_observations
    )



def test_collect_error_indices_combines_indices():
    result = collect_error_indices(
        [1, 2, 3],
        [3, 4, 5],
        [5, 6]
    )

    assert result == {1, 2, 3, 4, 5, 6}


def test_collect_error_indices_handles_empty_groups():
    result = collect_error_indices(
        [],
        [1, 2],
        []
    )

    assert result == {1, 2}


def test_collect_error_indices_without_arguments():
    result = collect_error_indices()

    assert result == set()



def test_filter_validated_data_removes_invalid_rows(sample_patients):
    error_indices = {1, 2}

    validated = filter_validated_data(
        sample_patients,
        error_indices
    )

    assert len(validated) == 2
    assert list(validated.index) == [0, 3]

    assert "patient_1" in validated["Id"].values
    assert "patient_4" in validated["Id"].values


def test_filter_validated_data_keeps_all_rows_when_no_errors(sample_patients):
    validated = filter_validated_data(
        sample_patients,
        set()
    )

    pd.testing.assert_frame_equal(
        validated,
        sample_patients
    )


def test_filter_validated_data_returns_copy(sample_patients):
    validated = filter_validated_data(
        sample_patients,
        {2}
    )

    validated.loc[0, "FIRST"] = "Changed"

    assert sample_patients.loc[0, "FIRST"] == "Anna"
