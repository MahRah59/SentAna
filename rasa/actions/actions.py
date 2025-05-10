from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import sqlite3
from rasa_sdk.events import SlotSet


class ActionShowProductInfo(Action):
    def name(self) -> str:
        return "action_show_product_info"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        product_name = tracker.get_slot('product_name')

        # Check if user is asking about all products
        intent = tracker.latest_message['intent'].get('name')
        if intent == "ask_about_all_products":
            try:
                conn = sqlite3.connect('/Users/MR_1/MyApplications/TestSentAna_CRM_Integrtion/instance/site.db')
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM Products")
                products = cursor.fetchall()
                product_list = ", ".join([product[0] for product in products])
                dispatcher.utter_message(text=f"We offer the following products: {product_list}.")
            except sqlite3.Error as e:
                dispatcher.utter_message(text=f"An error occurred while fetching the product list: {str(e)}")
            finally:
                conn.close()
            return []

        # Handle specific product inquiry
        if not product_name:
            dispatcher.utter_message(text="Could you please specify which product you're interested in? For example, speaker, laptop, or phone?")
            return []

        product_name = product_name.lower()
        try:
            conn = sqlite3.connect('/Users/MR_1/MyApplications/TestSentAna_CRM_Integrtion/instance/site.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Products WHERE lower(name) = ?", (product_name,))
            product = cursor.fetchone()

            if product:
                product_info = f"Product: {product[1]}\nSpecifications: {product[2]}\nRelease Date: {product[3]}\nPrice: {product[4]}"
                dispatcher.utter_message(text=f"Here are the details for {product_name}:\n{product_info}")
            else:
                dispatcher.utter_message(text=f"Sorry, I couldn't find information for {product_name}.")
        except sqlite3.Error as e:
            dispatcher.utter_message(text=f"An error occurred while fetching the product details: {str(e)}")
        finally:
            conn.close()

        return []



class ActionTrackOrder(Action):
    def name(self) -> str:
        return "action_track_order"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[Dict]:
        order_id = tracker.get_slot('order_id')

        if order_id:
            # Normalize to lowercase
            order_id = order_id.lower()

            conn = sqlite3.connect('/Users/MR_1/MyApplications/TestSentAna_CRM_Integrtion/instance/site.db')
            cursor = conn.cursor()

            cursor.execute("SELECT user_id, order_id, status , purchase_date, shipped_date, delivery_date, estimated_time FROM Delivery WHERE LOWER(order_id) = ?", (order_id,))
            order = cursor.fetchone()

            if order:
                dispatcher.utter_message(
                    text=f"User_id: {order[0]}\n Order Id: {order[1]}\n Status: {order[2]}\n Purchase_date: {order[3]}\n Shipped_date: {order[4]}\nDelivery_date: {order[5]}\n Estimated_time: {order[6]}"
                )
            else:
                dispatcher.utter_message(text=f"Sorry, no details found for order ID {order_id}.")

            conn.close()
        else:
            dispatcher.utter_message(text="I couldn't find your order ID. Please try again.")

        return [SlotSet("order_id", None)]




class ActionShowServices(Action):
    def name(self) -> str:
        return "action_show_services"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        service_type = tracker.get_slot('service_type')

        # Connect to the SQLite database
        conn = sqlite3.connect('/Users/MR_1/MyApplications/TestSentAna_CRM_Integrtion/instance/site.db')
        cursor = conn.cursor()

        if service_type:
            # Fetch specific service details
            service_type = service_type.lower()

            cursor.execute("SELECT id, description, availability, additional_information, service_type FROM Services WHERE lower(service_type)= ?", (service_type,))
            services = cursor.fetchall()
            if services:
                for service in services:
                    dispatcher.utter_message(
                        text=f"Service type: {service[4]}\nDescription: {service[1]}\nAvailability: {service[2]}\nAdditional information: {service[3]}"
)
            else:
                dispatcher.utter_message(text=f"Sorry, no details found for service type: {service_type}.")
        else:
            # Fetch all available services
            cursor.execute("SELECT service_type, description, availability FROM Services")
            services = cursor.fetchall()
            if services:
                service_list = "\n\n".join(
                    [f"Service Type: {service[0]}\nDescription: {service[1]}\nAvailability: {service[2]}" for service in services]
                )
                dispatcher.utter_message(text=f"Here are the available services:\n{service_list}")
            else:
                dispatcher.utter_message(text="No services are currently available.")

        conn.close()
        return []








"""

class ActionShowProductInfo(Action):
    def name(self) -> str:
        return "action_show_product_info"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        product_name = tracker.get_slot('product_name')

        # Check if user is asking about all products
        intent = tracker.latest_message['intent'].get('name')
        if intent == "ask_about_all_products":
            conn = None  # Initialize conn here to avoid the UnboundLocalError
            try:
                conn = sqlite3.connect('/Users/MR_1/MyApplications/TestSentAna_CRM_Integrtion/instance/site.db')
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM Products")
                products = cursor.fetchall()
                product_list = ", ".join([product[0] for product in products])
                dispatcher.utter_message(text=f"We offer the following products: {product_list}.")
            except sqlite3.Error as e:
                dispatcher.utter_message(text=f"An error occurred while fetching the product list: {str(e)}")
            finally:
                if conn:
                    conn.close()  # Close connection only if it was successfully initialized
            return []

        # Handle specific product inquiry
        if not product_name:
            dispatcher.utter_message(text="Could you please specify which product you're interested in? For example, speaker, laptop, or phone?")
            return []

        product_name = product_name.lower()
        conn = None  # Initialize conn here as well for the next try block
        try:
            conn = sqlite3.connect('/Users/BilloWill/MyApplications/TestSentAna_CRM_Integrtion/instance/site.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Products WHERE lower(name) = ?", (product_name,))
            product = cursor.fetchone()

            if product:
                product_info = f"Product: {product[1]}\nSpecifications: {product[2]}\nRelease Date: {product[3]}\nPrice: {product[4]}"
                dispatcher.utter_message(text=f"Here are the details for {product_name}:\n{product_info}")
            else:
                dispatcher.utter_message(text=f"Sorry, I couldn't find information for {product_name}.")
        except sqlite3.Error as e:
            dispatcher.utter_message(text=f"An error occurred while fetching the product details: {str(e)}")
        finally:
            if conn:
                conn.close()

        return []



class ActionTrackOrder(Action):
    def name(self) -> str:
        return "action_track_order"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[Dict]:
        order_id = tracker.get_slot('order_id')

        if order_id:
            # Normalize to lowercase
            order_id = order_id.lower()

            conn = sqlite3.connect('/Users/MR_1/MyApplications/TestSentAna_CRM_Integrtion/instance/site.db')
            cursor = conn.cursor()

            cursor.execute("SELECT order_id, status, estimated_time FROM Delivery WHERE LOWER(order_id) = ?", (order_id,))
            order = cursor.fetchone()

            if order:
                dispatcher.utter_message(
                    text=f"Order Id: {order[0]}\nStatus: {order[1]}\nEstimated Date: {order[2]}"
                )
            else:
                dispatcher.utter_message(text=f"Sorry, no details found for order ID {order_id}.")

            conn.close()
        else:
            dispatcher.utter_message(text="I couldn't find your order ID. Please try again.")

        return [SlotSet("order_id", None)]




class ActionShowServices(Action):
    def name(self) -> str:
        return "action_show_services"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        service_type = tracker.get_slot('service_type')

        # Connect to the SQLite database
        conn = sqlite3.connect('/Users/MR_1/MyApplications/TestSentAna_CRM_Integrtion/instance/site.db')
        cursor = conn.cursor()

        if service_type:
            # Fetch specific service details
            service_type = service_type.lower()

            cursor.execute("SELECT type, description, availability FROM Services WHERE lower(type)= ?", (service_type,))
            services = cursor.fetchall()
            if services:
                for service in services:
                    dispatcher.utter_message(
                        text=f"Service Type: {service[0]}\nDescription: {service[1]}\nAvailability: {service[2]}"
                    )
            else:
                dispatcher.utter_message(text=f"Sorry, no details found for service type: {service_type}.")
        else:
            # Fetch all available services
            cursor.execute("SELECT type, description, availability FROM Services")
            services = cursor.fetchall()
            if services:
                service_list = "\n\n".join(
                    [f"Service Type: {service[0]}\nDescription: {service[1]}\nAvailability: {service[2]}" for service in services]
                )
                dispatcher.utter_message(text=f"Here are the available services:\n{service_list}")
            else:
                dispatcher.utter_message(text="No services are currently available.")

        conn.close()
        return []

"""