# Chatbot Related Functions

import smtplib
from email.message import EmailMessage

import os
from email.message import EmailMessage
import smtplib
from dotenv import load_dotenv

from app import db
from app.models import ChatMessages
from datetime import datetime




import logging
logger = logging.getLogger(__name__)

# Load credentials from .env
load_dotenv()
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

########################################

def handle_escalation(user_id, message, escalation_flag):
    if escalation_flag == "high":
        # Send an email to support or sales, depending on the escalation type
        send_email_1(
            subject="Urgent: Escalation Required",
            recipient="support@company.com",
            body=f"User {user_id} has triggered an escalation. Message: {message}. Immediate attention needed."
        )
        


########################################
        


from twilio.rest import Client

def send_sms(to_phone_number, body):
    # Your Twilio credentials (get these from your Twilio account)

    from_phone_number = '+16267142788'

    # Initialize the Twilio client
    client = Client(account_sid, auth_token)

    try:
        # Send the SMS
        message = client.messages.create(
            body=body,
            from_=from_phone_number,
            to=to_phone_number
        )
        print(f"SMS sent successfully! Message SID: {message.sid}")
    except Exception as e:
        print(f"Error: {e}")

# Example usage
#send_sms('+46722445311', 'This is a test SMS.')   
########################################

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email_0(subject, body, to_email):
    # From email address (the company email or Gmail address)
    from_email = "your_email@example.com"
    
    # Define the SMTP server and port
    # For own server, replace with your SMTP server address
    smtp_server = "smtp.yourcompany.com"  # Example for own email server
    smtp_port = 587  # Typically 587 for TLS or 465 for SSL
    
    # Authentication credentials (use your email and password)
    smtp_username = "your_email_username"
    smtp_password = "your_email_password"
    
    # If using Gmail, update the SMTP server and credentials:
    # smtp_server = "smtp.gmail.com"  # Gmail's SMTP server
    # smtp_port = 587  # Gmail's TLS port
    # smtp_username = "your_gmail_address@gmail.com"
    # smtp_password = "your_gmail_password" (consider using OAuth2 instead of password for better security)

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach the email body to the email message
    msg.attach(MIMEText(body, 'plain'))

    # Send the email using SMTP
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection with TLS
            server.login(smtp_username, smtp_password)  # Authenticate
            text = msg.as_string()
            server.sendmail(from_email, to_email, text)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

########################################
        
import os
from email.message import EmailMessage
import smtplib
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

def send_email(subject, body, to_email):
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_HOST_USER
        msg['To'] = to_email

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.send_message(msg)

        print("✅ Email sent successfully.")

    except Exception as e:
        print(f"❌ Failed to send email: {e}")


########################################
        
        
def insert_chat_message(user_id, session_id, message_content, additional_info=None):
    try:
        chat_message = ChatMessages(
            user_id=user_id,
            session_id=session_id,
            message=message_content,
            timestamp=datetime.utcnow(),
            additional_info=additional_info
        )

        db.session.add(chat_message)
        db.session.commit()
        logger.debug(f"Inserted chat message for user {user_id} session {session_id}")
    except Exception as e:
        logger.error(f"Failed to insert chat message: {e}")
        db.session.rollback()


########################################

from app.models import ChatSessionSummary
from app import db
import logging

logger = logging.getLogger(__name__)

def create_chat_session_summary(
    user_id,
    session_id,
    timestamp,
    user_email,
    company_name,
    escalation_flag,
    total_user_messages,
    total_bot_messages,
    dominant_sentiment,
    sentiment_score,
    top_emotions,
    num_critical_messages,
    short_summary="Chat session summary",
    category="support"
):
    try:
        summary = ChatSessionSummary(
            user_id=user_id,
            session_id=session_id,
            timestamp=timestamp,
            user_email=user_email,
            company_name=company_name,
            category=category,
            short_summary=short_summary,
            escalation_flag=escalation_flag,
            total_user_messages=total_user_messages,
            total_bot_messages=total_bot_messages,
            total_messages=total_user_messages + total_bot_messages,
            dominant_sentiment=dominant_sentiment,
            sentiment_score=sentiment_score,
            top_emotions=top_emotions,
            num_critical_messages=num_critical_messages,
        )
        db.session.add(summary)
        db.session.commit()
        logger.info(f"✅ Chat session summary saved for session {session_id}")
        return True

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Failed to save chat session summary: {str(e)}")
        return False
########################################