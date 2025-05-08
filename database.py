import mysql.connector
import pandas as pd
from mysql.connector import Error
import os
from dotenv import load_dotenv
load_dotenv()

def get_db_connection():
    """Establish and return a database connection."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="manoj",
            database="college_predictor",
            autocommit=False
        )
        
        if connection.is_connected():
            print("✅ Successfully connected to the database.")
            return connection
    except Error as e:
        print(f"❌ Error while connecting to MySQL: {e}")
        return None

def populate_colleges():
    """Populate the 'colleges' and 'college_location' tables with bulk inserts."""
    conn = get_db_connection()
    if conn is None:
        return  # Stop if no connection could be established

    cursor = conn.cursor()

    # File paths for Excel data
    file_paths = [
        # r"C:\Users\manoj\Prodigy_Infotech_Internship\College predictor\clg predictor 3.0\college-predictor\backend\static\college_data\Round1.xlsx",
        # r"C:\Users\manoj\Prodigy_Infotech_Internship\College predictor\clg predictor 3.0\college-predictor\backend\static\college_data\Round2.xlsx",
        # r"C:\Users\manoj\Prodigy_Infotech_Internship\College predictor\clg predictor 3.0\college-predictor\backend\static\college_data\Round3.xlsx",
        r"C:\Users\manoj\Prodigy_Infotech_Internship\College predictor\clg predictor 3.0\college-predictor\backend\static\college_data\college_location.xlsx"
    ]

    try:
        for file_path in file_paths:
            df = pd.read_excel(file_path)

            # Clean column names
            df.columns = df.columns.str.upper().str.replace(' ', '_').str.replace('\n', '')

            print(f"📂 Processing file: {file_path}")

            # Bulk Insert for 'college_location'
            if 'CODE' in df.columns and 'COLLEGE_NAME' in df.columns and 'COLLEGE_DISTRICT' in df.columns:
                print("🔹 Bulk inserting into college_location")
                college_location_data = [
                    (row['CODE'], row['COLLEGE_NAME'], row['COLLEGE_DISTRICT'])
                    for _, row in df.iterrows()
                ]
                cursor.executemany(
                    """INSERT INTO college_location (code, college_name, college_district) VALUES (%s, %s, %s)""",
                    college_location_data
                )

            # Bulk Insert for 'colleges'
            elif 'AGGRMARK' in df.columns:
                print("🔹 Bulk inserting into colleges")
                colleges_data = [
                    (
                        row['COLLEGENAME'], row['BRANCHCODE'], row['COLLEGECODE'],
                        row['COMMUNITY'], validate_cutoff(row['AGGRMARK']),
                        row['DISTRICT'] if isinstance(row['DISTRICT'], str) else "Unknown",
                        row['COLLEGECODE']
                    )
                    for _, row in df.iterrows() if validate_cutoff(row['AGGRMARK']) is not None
                ]
                cursor.executemany(
                    """INSERT INTO colleges (college_name, branch, branch_code, community, average_cutoff, district, college_code) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    colleges_data
                )

        conn.commit()  # Commit all changes in one go
        print("🎉 Database updated successfully!")

    except Exception as e:
        conn.rollback()  # Rollback in case of errors
        print(f"❌ Error inserting data: {e}")

    finally:
        cursor.close()
        conn.close()

def validate_cutoff(value):
    """Validate and clean cutoff values."""
    try:
        return float(value) if pd.notnull(value) else None
    except ValueError:
        return None

if __name__ == "__main__":
    populate_colleges()
