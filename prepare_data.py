import pandas as pd
import numpy as np

dictionary = {
    'patients': ['Id', 'BIRTHDATE', 'FIRST', 'LAST', 'GENDER'],
    'encounters': ['Id', 'PATIENT', 'START', 'STOP', 'ENCOUNTERCLASS', 'DESCRIPTION', 'REASONCODE', 'REASONDESCRIPTION'],
    'observations': ['DATE', 'PATIENT', 'ENCOUNTER', 'CATEGORY', 'DESCRIPTION', 'VALUE', 'UNITS', 'TYPE'],
}

def load():
    patients = pd.read_csv('raw_data/patients.csv')
    encounters = pd.read_csv('raw_data/encounters.csv')
    observations = pd.read_csv('raw_data/observations.csv')
    dictionary_df = {
        'patients': patients,
        'encounters': encounters,
        'observations': observations,
    }
    return dictionary_df

def choose_columns(dictionary, dictionary_df):
    for df_name, columns in dictionary.items():
        dictionary_df[df_name] = dictionary_df[df_name][columns]
    return dictionary_df

def save_clean(dictionary_df_r):
    for df_name, df in dictionary_df_r.items():
        df.to_csv(f'clean_data/{df_name}.csv')

def purposeful_inconsistencies(dictionary_df_r):
    for df_name, df in dictionary_df_r.items():
        if df_name == 'patients':

            # Inconsistency n.1: Missing Id 
            df.loc[df['Id'] == 'f5749532-3295-ad01-d9b5-932c997e7a01', 'Id'] = pd.NA

            # Inconsistency n.2: Duplicate Id
            row_for_dup = df.loc[df['Id'] == '7132442e-b0b9-a886-e28d-f83700e5a3bd']
            df = pd.concat([df, row_for_dup], ignore_index=True)
            print(row_for_dup)
            

            dictionary_df_r[df_name] = df
    return dictionary_df_r

def main():
    dictionary_df = load()
    dictionary_df_r = choose_columns(dictionary, dictionary_df)
    print(dictionary_df_r['patients'].columns.tolist())

    save_clean(dictionary_df_r)
    dictionary_df_m = purposeful_inconsistencies(dictionary_df_r)
    print(dictionary_df_m['patients'].iloc[9])
    print(dictionary_df_m['patients'].iloc[108])

    # Updated DF of patients is one more record longer (the added duplicate)
    assert len(dictionary_df_r['patients']) == len(dictionary_df_r['patients']['Id'].unique()) + 1


if __name__ == '__main__':
    main()