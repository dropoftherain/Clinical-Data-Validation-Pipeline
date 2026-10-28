# Clinical-Data-Validation-Pipeline
Healthcare data pipeline using Synthea-generated synthetic patient data, Python, SQL, and pytest.

## Methodology 

### Data Resource: Synthea

[100 Sample Synthetic Patient Records, CSV](https://synthetichealth.github.io/synthea-sample-data/downloads/latest/synthea_sample_data_csv_latest.zip)

Jason Walonoski, Mark Kramer, Joseph Nichols, Andre Quina, Chris Moesel, Dylan Hall, Carlton Duffett, Kudakwashe Dube, Thomas Gallagher, Scott McLachlan, Synthea: An approach, method, and software mechanism for generating synthetic patients and the synthetic electronic health care record, Journal of the American Medical Informatics Association, Volume 25, Issue 3, March 2018, Pages 230–238, https://doi.org/10.1093/jamia/ocx079


### Original Data
- three tables with following chosen variables: 

| File | Columns |
| --- | --- |
| `patients.csv` | Id, BIRTHDATE, FIRST, LAST, GENDER |
| `encounters.csv` | Id, PATIENT, START, STOP, ENCOUNTERCLASS, DESCRIPTION, REASONCODE, REASONDESCRIPTION |
| `observations.csv` | DATE, PATIENT, ENCOUNTER, CATEGORY, DESCRIPTION, VALUE, UNITS, TYPE |

### Purposeful Inconsistencies

| Inconsistency | DataFrame | Index | What is wrong |
|---|---|---|---|
| 1 | patients | 9 | Missing Id |
| 2 | patients | 108 (last appended row) | Duplicate Id |
| 3 | encounters | 1 | Missing START |
| 4 | encounters | 19 | Invalid PATIENT ID |
| 5 | encounters | 0 | START and STOP switched |
| 6 | observations | 965 | Invalid ENCOUNTER ID |
| 7 | observations | 203 | VALUE does not match expected numeric type |

### File Repository

## Results

### Patients Report

| Validation rule number | Validation rule | DataFrame | Inconsistency detected? | Inconsistency number | Affected rows | Investigation status |
|---|---|---|---|---|---|---|
| Validation rule 1 | `Id` cannot be null | patients | Yes | 1 | 1 (index 9) | Expected — intentional. Missing `Id` at index 9. |
| Validation rule 2 | `Id` cannot be duplicated | patients | Yes | 2 | 1 (index 108; duplicate of an existing ID) | Expected — intentional. Duplicate `Id` at index 108. |
| Validation rule 3 | `Id` must be a valid UUID | patients | - | - | - | No findings reported. |
| Validation rule 4 | `BIRTHDATE` cannot be null | patients | - | - | - | No findings reported. |
| Validation rule 5 | `BIRTHDATE` must be a valid date | patients | - | - | - | No findings reported. |
| Validation rule 6 | `BIRTHDATE` must not be in the future | patients | - | - | - | No findings reported. |
| Validation rule 7 | `FIRST` cannot be null | patients | - | - | - | No findings reported. |
| Validation rule 8 | `LAST` cannot be null | patients | - | - | - | No findings reported. |
| Validation rule 9 | `GENDER` cannot be null | patients | - | - | - | No findings reported. |
| Validation rule 10 | `GENDER` must belong to the allowed set | patients | - | - | - | No findings reported. |

### Encounters Report

| Validation rule number | Validation rule | DataFrame | Inconsistency detected? | Inconsistency number | Affected rows | Investigation status |
|---|---|---|---|---|---|---|
| Validation rule 11 | `Id` cannot be null | encounters | - | - | - | No findings reported. |
| Validation rule 12 | `Id` cannot be duplicated | encounters | - | - | - | No findings reported. |
| Validation rule 13 | `Id` must be a valid UUID | encounters | - | - | - | No findings reported. |
| Validation rule 14 | `PATIENT` cannot be null | encounters | - | - | - | No findings reported. |
| Validation rule 15 | `PATIENT` must reference an existing patient | encounters | Yes | 1, 4 | 37 records | Explained — 36 downstream failures caused by inconsistency 1, where patient Id was removed from `patients`, plus 1 intentional inconsistency 4 at index 19. |
| Validation rule 16 | `START` cannot be null | encounters | Yes | 3 | 1 (index 1) | Expected — intentional. Missing `START` at index 1. |
| Validation rule 17 | `START` must be a valid datetime | encounters | - | - | - | No findings reported. |
| Validation rule 18 | `STOP`, if present, must be a valid datetime | encounters | - | - | - | No findings reported. |
| Validation rule 19 | `STOP` must not be before `START` | encounters | Yes | 5 | 1 (index 0) | Expected — intentional. `START` and `STOP` were switched at index 0. |

### Observations Report

| Validation rule number | Validation rule | DataFrame | Inconsistency detected? | Inconsistency number | Affected rows | Investigation status |
|---|---|---|---|---|---|---|
| Validation rule 20 | `DATE` cannot be null | observations | - | - | - | No findings reported. |
| Validation rule 21 | `DATE` must be a valid datetime | observations | - | - | - | No findings reported. |
| Validation rule 22 | `PATIENT` cannot be null | observations | - | - | - | No findings reported. |
| Validation rule 23 | `PATIENT` must reference an existing patient | observations | Yes | 1 | 397 records | Explained — downstream effect of the patient ID removed from `patients`. These records reference a patient ID that no longer exists in the parent table. |
| Validation rule 24 | `ENCOUNTER`, if present, must reference an existing encounter | observations | Yes | 6 | 1 (index 965) | Expected — intentional. Invalid `ENCOUNTER` ID at index 965. |
| Validation rule 25 | `CATEGORY` cannot be null | observations | Yes | External | 3,060 unique records | Observed — records associated with QALY, DALY, QOLS, or similar measures have missing categories. Requires confirmation against source data expectations. |
| Validation rule 26 | `CATEGORY` must belong to the allowed set | observations | - | - | - | No findings reported. |
| Validation rule 27 | `VALUE` cannot be null | observations | - | - | - | No findings reported. |
| Validation rule 28 | `TYPE` cannot be null | observations | - | - | - | No findings reported. |
| Validation rule 29 | `TYPE` must correspond to the datatype of `VALUE` | observations | Yes | 7, External | 1 intentional record (index 203); 1,001 additional records requiring investigation | Expected — intentional mismatch at index 203 (`VALUE = 'eighty'`, `TYPE = 'numeric'`). The other 1,001 mismatches are not explained by the intentional inconsistencies. Their values appear numeric, and they should describe numerical observations. |


