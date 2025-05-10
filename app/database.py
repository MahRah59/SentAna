# database.py
import sqlite3
from datetime import datetime


import sqlite3

def find_SentAna_user(first_name, last_name, email):
    try:
        conn = sqlite3.connect('/Users/MR_1/MyApplications/TestSentAna_CRM_Integrtion/instance/site.db')
        cursor = conn.cursor()

        query = """
                SELECT *
                FROM user
                WHERE first_name = ?
                AND last_name = ?
                AND email = ?;
            """

        cursor.execute(query, (first_name, last_name, email))
        result = cursor.fetchone()  # Fetch the first matching row
        if result:
            print("There is a user .......")

        conn.close()
        return result

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None


"""
# Example usage
user_data = get_user('Olle', 'Svensson', 'Olle.svensson@example.se')

if user_data:
    print("User found:", user_data)
else:
    print("User not found.")

    """