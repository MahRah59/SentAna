
"""
import sqlite3

# Connect to the source database (old_10_Chatbot_SentimentAnalysis)
source_conn = sqlite3.connect('/Users/MR_1/MyApplications/old_10_Chatbot_SentimentAnalysis/instance/site.db')
source_cursor = source_conn.cursor()

# Connect to the destination database (TestSentAna_CRM_Integrtion)
destination_conn = sqlite3.connect('/Users/MR_1/MyApplications/TestSentAna_CRM_Integrtion/instance/site.db')
destination_cursor = destination_conn.cursor()

# Function to copy a table from source to destination
def copy_table(table_name):
    temp_columns=[]
    # Fetch the schema (structure) of the table
    source_cursor.execute(f"PRAGMA table_info({table_name});")
    columns = source_cursor.fetchall()
    if columns:
        temp_columns[0]= columns[0]
        temp_columns[1]= columns[2]
        temp_columns[2]= columns[3]
        temp_columns[3] = ""
        temp_columns[4]= columns[1]


    # Create the table in the destination database with the same structure
    column_defs = ', '.join([f"{column[1]} {column[2]}" for column in columns])
    destination_cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({column_defs});")
    
    # Copy data from the source table to the destination table
    source_cursor.execute(f"SELECT * FROM {table_name};")
    rows = source_cursor.fetchall()
    destination_cursor.executemany(f"INSERT INTO {table_name} VALUES ({', '.join(['?'] * len(temp_columns))})", rows)

    # Commit the changes
    destination_conn.commit()
    print(f"Table {table_name} copied successfully!")

# List of tables to copy
tables_to_copy = ['Delivery', 'Services', 'Products']

# Copy each table
#for table in tables_to_copy:
copy_table('Services')

# Close both connections
source_conn.close()
destination_conn.close()



"""

import sqlite3

def copy_table(source_db_path, destination_db_path, table_name):
    """
    Copies data from a source table to a destination table with different column order.

    Args:
        source_db_path (str): Path to the source database file.
        destination_db_path (str): Path to the destination database file.
        table_name (str): Name of the table to copy.

    Returns:
        None
    """

    try:
        # Connect to both databases
        source_conn = sqlite3.connect(source_db_path)
        destination_conn = sqlite3.connect(destination_db_path)
        source_cursor = source_conn.cursor()
        destination_cursor = destination_conn.cursor()

        # Define column mapping (source index -> destination index)
        column_mapping = {
            0: 4,  # Source column 0 to destination column 4
            1: 1,  # Source column 1 to destination column 1
            2: 2,  # Source column 2 to destination column 2
            3: 0   # Source column 3 to destination column 0 
        }

        # Get column names from source table
        source_cursor.execute(f"PRAGMA table_info({table_name});")
        source_columns = source_cursor.fetchall()
        source_column_names = [row[1] for row in source_columns]

        # Get column names from destination table
        destination_cursor.execute(f"PRAGMA table_info({table_name});")
        destination_columns = destination_cursor.fetchall()
        destination_column_names = [row[1] for row in destination_columns]

        # Create insert statement with correct column order
        insert_sql = f"INSERT INTO {table_name} ({','.join(destination_column_names)}) VALUES ({','.join(['?'] * len(destination_column_names))})"

        # Fetch data from source table
        source_cursor.execute(f"SELECT * FROM {table_name}")
        data = source_cursor.fetchall() 

        # Insert data into destination table with correct column order
        for row in data:
            rearranged_row = [row[source_index] for source_index in column_mapping]
            rearranged_row.insert(3, "default_value")  # Insert default value at index 3
            destination_cursor.execute(insert_sql, rearranged_row)

        destination_conn.commit()

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        source_conn.close()
        destination_conn.close()

# Example usage:
source_db_path = '/Users/MR_1/MyApplications/old_10_Chatbot_SentimentAnalysis/instance/site.db'
destination_db_path = '/Users/MR_1/MyApplications/TestSentAna_CRM_Integrtion/instance/site.db'
table_name = 'Services'

copy_table(source_db_path, destination_db_path, table_name)
