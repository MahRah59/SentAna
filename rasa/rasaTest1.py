from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Tracker
from rasa_sdk.events import SlotSet

# Import your custom action
from actions import ActionProductInfo
from actions.actions import ActionProductInfo


import sqlite3

from typing import Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import sqlite3

from typing import Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import sqlite3

# Define the query
query = "SELECT status, estimated_time FROM Delivery WHERE LOWER(order_id) = ?"

# Example usage
db_path = '/Users/mahmoudrahmani/MyApplications/TestSentimentAnalysis/instance/site.db'
order_id = "order123"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(query, (order_id.lower(),))
    result = cursor.fetchone()
    print(f"Query result: {result}")
    print(f"Using database path: {db_path}")
    print(f"The detaisl for Order ID'{order_id}':\n")
    print(f"Status:{result[0]}\n")
    print(f"Delivery time:{result[1]}\n")


    if result:
        response = (
        f"The details for Order ID '{order_id}':\n"
        f"Status: {result[0]}\n"
        f"Estimated Delivery Time: {result[1]}"
                    )
    else:
        response = f"Sorry, I couldn't find details for Order ID '{order_id}'."

    conn.close()
except Exception as e:
    print(f"Error: {e}")


