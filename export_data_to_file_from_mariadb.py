#!/usr/bin/env python3

import mysql.connector
import csv
import logging
import subprocess
import os
from datetime import datetime
from dotenv import load_dotenv

from calc_date_time import file_creation_datetime

load_dotenv()


def run_send_mail_script():
    try:
        subprocess.run(['python3', 'send_mail.py'], check=True)
        # print("Send mail script executed successfully.")
    except subprocess.CalledProcessError as e:
        # print(f"Error running send mail script: {e}")
        logging.exception(f"Error running send mail script: {e}")


def append_to_log_file(log_message, log_file):
    with open(log_file, "a") as log_file:
        log_file.write(f"\n### {datetime.now()}\n{log_message}")


user = os.getenv("user")
password = os.getenv("password")
host = os.getenv("host")
database = os.getenv("database")
export_file_name = os.getenv("export_file_name")
log_file = f"./script_log_{file_creation_datetime}.log"

# Define the database connection details
config = {
    'user': user,
    'password': password,
    'host': host,
    'database': database
}

conn = None
cursor = None

try:
    # Establish the database connection
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    # Define the SELECT query
    query = "select sysname,hostname,hardware,serial,features,os,version from devices;"

    # Execute the SELECT query
    cursor.execute(query)

    # Fetch all the rows from the executed query
    rows = cursor.fetchall()

    # Get the column names
    column_names = [i[0] for i in cursor.description]

    # Define the output file path
    output_file_path = f'{export_file_name}_{file_creation_datetime}.csv'

    # Write the fetched data to the output file
    with open(output_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(column_names)  # Write the column headers
        writer.writerows(rows)  # Write the rows

    log_message = f"Data has been successfully saved to {output_file_path}"
    append_to_log_file(log_message, log_file)
    # print(log_message)

except mysql.connector.Error as err:
    append_to_log_file(err, log_file)
    # print(f"Error: {err}")

finally:
    # Close the cursor and connection
    if cursor:
        cursor.close()
    if conn:
        conn.close()

run_send_mail_script()
