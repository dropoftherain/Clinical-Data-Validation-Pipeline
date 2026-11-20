import psycopg2
import os
import pandas as pd
import numpy as np
from prepare_data import load

sql_create_patients = '''CREATE TABLE patients(id SERIAL PRIMARY KEY,
                                patient_id UUID NOT NULL UNIQUE,
                                birthdate DATE,
                                first_name VARCHAR(100),
                                last_name VARCHAR(100),
                                gender VARCHAR(1)
                                );
    '''

sql_create_encounters = '''CREATE TABLE encounters(id SERIAL PRIMARY KEY,
                                encounter_id UUID NOT NULL UNIQUE,
                                patient_id UUID NOT NULL,
                                start_time TIMESTAMPTZ,
                                stop_time TIMESTAMPTZ,
                                encounter_class VARCHAR(20),
                                description VARCHAR(255),
                                reason_code REAL,
                                reason_description VARCHAR(255)
                                );
    '''

sql_create_observations = '''CREATE TABLE observations(id SERIAL PRIMARY KEY,
                                patient_id UUID NOT NULL,
                                encounter_id UUID NOT NULL,
                                date TIMESTAMPTZ,
                                category VARCHAR(20),
                                description VARCHAR(255),
                                value VARCHAR(255),
                                units VARCHAR(20),
                                type VARCHAR(20)
                                );
        '''

sql_tables_to_be_created = [sql_create_patients, sql_create_encounters, sql_create_observations]

sql_insert_patient = '''
            INSERT INTO patients(patient_id, birthdate, first_name, last_name, gender)
            VALUES (%s, %s, %s, %s, %s);
        '''

sql_insert_encounter = '''
            INSERT INTO encounters(encounter_id, patient_id, start_time, stop_time, encounter_class, description, reason_code, reason_description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        '''

sql_insert_observation = '''
            INSERT INTO observations(patient_id, encounter_id, date, category, description, value, units, type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        '''

def create_tables(cursor):
    """Drop and recreate patients, encounters, and observations tables."""
    cursor.execute('''DROP TABLE IF EXISTS observations''')
    cursor.execute('''DROP TABLE IF EXISTS encounters''')
    cursor.execute('''DROP TABLE IF EXISTS patients''')

    for sql in sql_tables_to_be_created:
        cursor.execute(sql)

def insert_data(sql_insert, cursor, df, index_switch: bool):
    """Insert each dataframe row using sql_insert.

    When index_switch is True, reorder observation columns so DATE comes
    after the foreign keys (CSV order differs from the INSERT column order).
    """
    if index_switch == True:
        idx = [1, 2, 0, 3, 4, 5, 6, 7]
    for i, row in df.iterrows():
        arr = np.array(df)[i]
        cursor.execute(sql_insert, arr if index_switch == False else arr[idx])

def main():
    """Load validated_data/ into the local PostgreSQL clinical_data database."""
    data = load("validated_data")

    patients = data['patients']
    encounters = data['encounters']
    observations = data['observations']

    db_password = os.getenv("DB_PASSWORD")

    conn = psycopg2.connect(
        database="clinical_data",
        user="postgres",
        password=db_password,
        host="localhost",
        port="5434"
    )
    print("Connection successful")

    # conn.autocommit = True
    cursor = conn.cursor()

    create_tables(cursor=cursor)

    insert_data(sql_insert_patient, cursor, patients, index_switch=False)
    insert_data(sql_insert_encounter, cursor, encounters, index_switch=False)
    insert_data(sql_insert_observation, cursor, observations, index_switch=True)

    conn.commit()
    cursor.execute('''SELECT * FROM patients;''')

    conn.close()

if __name__ == '__main__':
    main()