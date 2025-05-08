import mysql.connector
import pandas as pd
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Establish and return a database connection."""
    try:
        conn = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE"),
            port=int(os.getenv("MYSQL_PORT"))
        )
        if conn.is_connected():
            print("✅ Successfully connected to MySQL!")
            cursor = conn.cursor()
            cursor.execute("SHOW DATABASES;")
            databases = cursor.fetchall()
            print("📂 Available Databases:", databases)
            
            cursor.close()
            conn.close()
        else:
            print("❌ Connection failed.")
    except Error as e:
        print(f"❌ Error while connecting to MySQL: {e}")
        return None

if __name__ == "__main__":
    get_db_connection()

