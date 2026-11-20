import pandas as pd
import pytest

from prepare_data import (
    load,
    choose_columns,
    purposeful_inconsistencies,
    RAW_DIR,
    CLEAN_DIR,
    TEST_DIR,
)

@pytest.mark.parametrize(
    "step",
    [RAW_DIR, CLEAN_DIR, TEST_DIR],
)
def test_load_existing_data(step):
    result = load(step)

    assert isinstance(result, dict)
    assert set(result.keys()) == {
        "patients",
        "encounters",
        "observations",
    }

def test_load_not_existing_data():
    with pytest.raises(FileNotFoundError):
        load("not_existing")

@pytest.mark.parametrize(
    "dict_w_columns, dict_w_df",
    [
        ({"df_test": ['Id', 'PATIENTS']}, {"df_test": pd.DataFrame(columns=['Id', 'PATIENTS', 'Column_To_Cut'])})
    ]
)
def test_choose_columns(dict_w_columns, dict_w_df):
    result = choose_columns(dict_w_columns, dict_w_df)

    assert isinstance(result, dict)
    assert result["df_test"].columns.tolist() == dict_w_columns["df_test"]

@pytest.fixture
def test_data():
    patients = pd.DataFrame({
        "Id": [
            "f5749532-3295-ad01-d9b5-932c997e7a01",
            "7132442e-b0b9-a886-e28d-f83700e5a3bd",
        ],
        "BIRTHDATE": ["1980-01-01", "1990-05-10"],
        "FIRST": ["Anna", "Peter"],
        "LAST": ["Test", "Example"],
        "GENDER": ["F", "M"],
    })

    encounters = pd.DataFrame({
        "Id": [
            "cc3eac4a-34a7-9a15-13f3-57f4a6b934f9",
            "cc3eac4a-34a7-9a15-1dc5-a353457420c6",
            "8b9df7af-24b3-66ee-d46c-520a00b76fa8",
        ],
        "PATIENT": [
            "7132442e-b0b9-a886-e28d-f83700e5a3bd",
            "7132442e-b0b9-a886-e28d-f83700e5a3bd",
            "7132442e-b0b9-a886-e28d-f83700e5a3bd",
        ],
        "START": [
            "2024-01-01T10:00:00Z",
            "2024-01-02T10:00:00Z",
            "2024-01-03T10:00:00Z",
        ],
        "STOP": [
            "2024-01-01T11:00:00Z",
            "2024-01-02T11:00:00Z",
            "2024-01-03T11:00:00Z",
        ],
        "ENCOUNTERCLASS": ["ambulatory"] * 3,
        "DESCRIPTION": ["Test"] * 3,
        "REASONCODE": ["123"] * 3,
        "REASONDESCRIPTION": ["Test reason"] * 3,
    })

    observations = pd.DataFrame({
        "DATE": ["2024-01-01", "2024-01-02"],
        "PATIENT": [
            "65cbad6a-eb9d-420e-9bab-b4f9c6aab7db",
            "cc3eac4a-34a7-9a15-1522-8087135631b7",
        ],
        "ENCOUNTER": [
            "65cbad6a-eb9d-420e-0c28-4eb837f969bc",
            "cc3eac4a-34a7-9a15-0045-5d8e18d8dd42",
        ],
        "CATEGORY": ["survey", "vital-signs"],
        "DESCRIPTION": [
            "Generalized anxiety disorder 7 item (GAD-7) total score [Reported.PHQ]",
            "Diastolic Blood Pressure",
        ],
        "VALUE": ["5", "80"],
        "UNITS": ["score", "mmHg"],
        "TYPE": ["numeric", "numeric"],
    })

    return {
        "patients": patients,
        "encounters": encounters,
        "observations": observations,
    }

def test_purposeful_inconsistencies(test_data):
    original_data = {
        name: df.copy(deep=True)
        for name, df in test_data.items()
    }
    result_dict = purposeful_inconsistencies(test_data)

    # 1. Missing patient Id
    assert pd.isna(result_dict["patients"].loc[0, "Id"])

    # 2. Duplicate patient Id
    assert result_dict["patients"].loc[1, "Id"] == result_dict["patients"].loc[2, "Id"]
    assert result_dict["patients"]["Id"].duplicated().sum() == 1
    assert len(result_dict["patients"]) == 3

    # 3. Missing START
    assert pd.isna(result_dict["encounters"].loc[1, "START"])

    # 4. Invalid patient Id
    assert (result_dict["encounters"].loc[2, "PATIENT"] == "8b9df7af-24b3-66ee-afeb-2734ebcbd33a")

    # 5. Switched START and END
    assert original_data["encounters"].iloc[0]["START"] == result_dict["encounters"].iloc[0]["STOP"]
    assert original_data["encounters"].iloc[0]["STOP"] == result_dict["encounters"].iloc[0]["START"]

    # 6. Invalid encounter Id
    assert (result_dict["observations"].loc[0, "ENCOUNTER"] == "65cbad6a-eb9d-420e-0c28-4eb837f969bz")

    # 7. VALUE does not correspond to TYPE
    assert result_dict["observations"].loc[1, "VALUE"] == "eighty"
