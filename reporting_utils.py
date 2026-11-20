import pandas as pd

def make_report(df, df_name, reason_dict):
    """Build a list of failing rows, one entry per (row, reason) pair."""
    report = []
    columns = df.columns

    for reason, invalid_Ids in reason_dict.items():  
        invalid_list = [{'DF': df_name,
                         'Index': i,
                        **{column: df.at[i, column] for column in columns},
                        'Reason': reason} for i in invalid_Ids]
        report.extend(invalid_list)
    return report

def make_dictionary(df_patients, df_encounters, df_observations):
    """Wrap the three tables in a name → DataFrame mapping."""
    dictionary = {
            'patients': pd.DataFrame(df_patients),
            'encounters': pd.DataFrame(df_encounters),
            'observations': pd.DataFrame(df_observations)
        }
    
    return dictionary

def collect_error_indices(*index_groups):
    """Union several index groups into one set of failing row indices."""
    all_indices = set()

    for indices in index_groups:
        all_indices.update(indices)

    return all_indices

def filter_validated_data(df, error_indices):
    """Return a copy of df excluding rows whose index is in error_indices."""
    return df.loc[~df.index.isin(error_indices)].copy()