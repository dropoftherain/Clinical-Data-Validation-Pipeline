import os
import pandas as pd
import numpy as np

dictionary = {
    'patients': ['Id', 'BIRTHDATE', 'FIRST', 'LAST', 'GENDER'],
    'encounters': ['Id', 'PATIENT', 'START', 'STOP', 'ENCOUNTERCLASS', 'DESCRIPTION', 'REASONCODE', 'REASONDESCRIPTION'],
    'observations': ['DATE', 'PATIENT', 'ENCOUNTER', 'CATEGORY', 'DESCRIPTION', 'VALUE', 'UNITS', 'TYPE'],
}

# Pipeline stage folders under data/
RAW_DIR = os.path.join('data', 'raw')
CLEAN_DIR = os.path.join('data', 'clean')
TEST_DIR = os.path.join('data', 'test')
VALIDATED_DIR = os.path.join('data', 'validated')
REPORTS_DIR = os.path.join('data', 'reports')

def load(step_in_the_process: str):
    """Load patients, encounters, and observations CSVs from a pipeline folder."""
    dictionary_df = {}
    for file in ['patients', 'encounters', 'observations']:
        df = pd.read_csv(f'{step_in_the_process}/{file}.csv')
        dictionary_df[file] = df

    return dictionary_df

def choose_columns(dictionary, dictionary_df):
    """Keep only the configured columns for each dataframe."""
    for df_name, columns in dictionary.items():
        dictionary_df[df_name] = dictionary_df[df_name][columns]

    return dictionary_df

def save_data(dictionary_df, step_in_the_process: str):
    """Write each dataframe as a CSV into the given folder (created if missing)."""
    os.makedirs(step_in_the_process, exist_ok=True)
    for df_name, df in dictionary_df.items():
        df.to_csv(f'{step_in_the_process}/{df_name}.csv', index=False)

def purposeful_inconsistencies(dictionary_df):
    """Inject the seven intentional data-quality faults used for validation testing."""
    for df_name, df in dictionary_df.items():
        if df_name == 'patients':

            # Inconsistency n.1: Missing Id (patients)
            df.loc[df['Id'] == 'f5749532-3295-ad01-d9b5-932c997e7a01', 'Id'] = pd.NA

            # Inconsistency n.2: Duplicate Id (patients)
            row_for_dup = df.loc[df['Id'] == '7132442e-b0b9-a886-e28d-f83700e5a3bd']
            df = pd.concat([df, row_for_dup], ignore_index=True)
            print(row_for_dup)

        if df_name == 'encounters':

            # Inconsistency n.3: Missing start (encounters)
            df.loc[df['Id'] == 'cc3eac4a-34a7-9a15-1dc5-a353457420c6', 'START'] = pd.NA # Index 1

            # Inconsistency n.4: Invalid patient Id (encounters)
            df.loc[df['Id'] == '8b9df7af-24b3-66ee-d46c-520a00b76fa8', 'PATIENT'] = '8b9df7af-24b3-66ee-afeb-2734ebcbd33a' # Index 19
            
            # Inconsistency n.5: Start and end time switched (encounters)
            start_for_switch = df.loc[df['Id'] == 'cc3eac4a-34a7-9a15-13f3-57f4a6b934f9', 'START'] # Index 0
            stop_for_switch = df.loc[df['Id'] == 'cc3eac4a-34a7-9a15-13f3-57f4a6b934f9', 'STOP']
            df.loc[df['Id'] == 'cc3eac4a-34a7-9a15-13f3-57f4a6b934f9', 'START'] = stop_for_switch
            df.loc[df['Id'] == 'cc3eac4a-34a7-9a15-13f3-57f4a6b934f9', 'STOP'] = start_for_switch

        if df_name == 'observations':
        
            # Inconsistency n.6: Invalid encounter Id (observations) # Index 965
            df.loc[
                (df['PATIENT'] == '65cbad6a-eb9d-420e-9bab-b4f9c6aab7db')
                & (df['ENCOUNTER'] == '65cbad6a-eb9d-420e-0c28-4eb837f969bc')
                & (df['DESCRIPTION'] == 'Generalized anxiety disorder 7 item (GAD-7) total score [Reported.PHQ]'), 'ENCOUNTER'
            ] = '65cbad6a-eb9d-420e-0c28-4eb837f969bz' # Index 965
            
            # Inconsistency n.7: Type does not correspond to the value (observations) # Index 203
            df.loc[
                (df['PATIENT'] == 'cc3eac4a-34a7-9a15-1522-8087135631b7')
                & (df['ENCOUNTER'] == 'cc3eac4a-34a7-9a15-0045-5d8e18d8dd42')
                & (df['DESCRIPTION'] == 'Diastolic Blood Pressure'), 'VALUE'
            ] = 'eighty' # Index 203

        dictionary_df[df_name] = df
            
    return dictionary_df

def main():
    """Build data/clean/ from data/raw/, then write data/test/ with intentional faults."""
    dictionary_df = load(RAW_DIR)
    dictionary_df_c = choose_columns(dictionary, dictionary_df)
    print('Selected columns of patients dataframe: ', dictionary_df_c['patients'].columns.tolist())

    save_data(dictionary_df_c, CLEAN_DIR)

    # Create independent copies for testing
    dictionary_df_t = {
        df_name: df.copy(deep=True)
        for df_name, df in dictionary_df_c.items()
    }

    dictionary_df_t = purposeful_inconsistencies(dictionary_df_t)

    # Double-check changes on patients DF
    print('Patient with missing Id: ', dictionary_df_t['patients'].iloc[9]) # Inconsistency n.1
    print('Duplicated PATIENT: ', dictionary_df_t['patients'].iloc[108]) # Inconsistency n.2

    # Updated DF is one more record longer (the added duplicate)
    assert len(dictionary_df_t['patients']) == len(dictionary_df_t['patients']['Id'].unique()) + 1

    # Double-check changes on encounters DF
    print('Encounter with missing START: ', dictionary_df_t['encounters'].iloc[1]) # Inconsistency n.3
    print('Encounter with invalid PATIENT Id: ', dictionary_df_t['encounters'].iloc[19]) # Inconsistency n.4
    print('Encounter with switched START and STOP: ', dictionary_df_t['encounters'].iloc[0]) # Inconsistency n.5

    # Double-check changes on observations DF
    print('Observation with invalid ENCOUNTER: ', dictionary_df_t['observations'].iloc[965]) # Inconsistency n.6
    print('Observation with not corresponding VALUE/TYPE: ', dictionary_df_t['observations'].iloc[203]) # Inconsistency n.7

    save_data(dictionary_df_t, TEST_DIR)

if __name__ == '__main__':
    main()