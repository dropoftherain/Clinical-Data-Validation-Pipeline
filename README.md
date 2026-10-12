# Clinical-Data-Validation-Pipeline
Healthcare data pipeline using Synthea-generated synthetic patient data, Python, SQL, and pytest.

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


### Data Resource: Synthea

[100 Sample Synthetic Patient Records, CSV](https://synthetichealth.github.io/synthea-sample-data/downloads/latest/synthea_sample_data_csv_latest.zip)

Jason Walonoski, Mark Kramer, Joseph Nichols, Andre Quina, Chris Moesel, Dylan Hall, Carlton Duffett, Kudakwashe Dube, Thomas Gallagher, Scott McLachlan, Synthea: An approach, method, and software mechanism for generating synthetic patients and the synthetic electronic health care record, Journal of the American Medical Informatics Association, Volume 25, Issue 3, March 2018, Pages 230–238, https://doi.org/10.1093/jamia/ocx079
