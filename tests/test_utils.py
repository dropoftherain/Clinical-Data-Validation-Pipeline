import pandas as pd
import pytest

from utils import (
    is_valid_uuid,
    is_valid_date,
    is_valid_datetime,
    check_datatype,
)

@pytest.mark.parametrize(
    "value, expected",
    [
        ("f5749532-3295-ad01-d9b5-932c997e7a01", True),
        ("65cbad6a-eb9d-420e-0c28-4eb837f969bz", False), # Contains z, while UUID allows only a-f (or A-F)
        (None, False),
        ("", False),
    ],
)
def test_uuid_validation(value, expected):
    assert is_valid_uuid(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("1980-01-01", True),
        ("2024-02-30", False),
        ("not-a-date", False),
        (None, False),
    ],
)
def test_date_validation(value, expected):
    assert is_valid_date(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("2024-01-15T10:30:00Z", True),
        ("2024-01-15T10:30:00+01:00", True),
        ("not-a-datetime", False),
        (None, False),
    ],
)
def test_datetime_validation(value, expected):
    assert is_valid_datetime(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("120", "numeric"),
        ("12.5", "numeric"),
        ("eighty", "text"),
        (None, "missing"),
        (pd.NA, "missing")
    ],
)
def test_check_datatype(value, expected):
    assert check_datatype(value) == expected
