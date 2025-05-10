# app/models.py

from app import db
from flask_login import UserMixin
from flask import session
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


now = datetime.now()

current_time = now.strftime("%H:%M:%S")

##########################################

class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), default="customer")
    password_hash = db.Column(db.String(60), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    company = db.Column(db.String(100), nullable=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_crm_contact = db.Column(db.Boolean, default=False)
    crm_contact_id = db.Column(db.String(255))
    image_file = db.Column(db.String(20), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)


    # Relationships
    deliveries = db.relationship('Delivery', back_populates='user', lazy=True)
    chat_messages = db.relationship('ChatMessages', back_populates='user', lazy=True)  # renamed

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

##########################################
    
    
class ChatMessages(db.Model):
    __tablename__ = 'chatMessages'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(    
    db.Integer,
    db.ForeignKey('user.id', name='fk_user_delivery'),
    nullable=False
    )    
    #user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key linking to User

    session_id = db.Column(db.Integer, nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    additional_info = db.Column(db.String(500))

    # Define the relationship to User
    #user = db.relationship('User', backref='chat_messages')  # Unique backref name
    user = db.relationship('User', back_populates='chat_messages')


    def __repr__(self):
        return f"Test_ChatMessages('{self.user_id}', '{self.session_id}', '{self.timestamp}')"


##########################################
    
class ChatSessionSummary(db.Model):
    __tablename__ = 'chat_session_summary'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_id = db.Column(db.String, nullable=False, unique=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    user_email = db.Column(db.String(120))
    company_name = db.Column(db.String(120))

    category = db.Column(db.String(50))
    short_summary = db.Column(db.String(300))
    escalation_flag = db.Column(db.String(10))

    total_user_messages = db.Column(db.Integer)
    total_bot_messages = db.Column(db.Integer)
    total_messages = db.Column(db.Integer)

    dominant_sentiment = db.Column(db.String(20))
    sentiment_score = db.Column(db.Float)

    top_emotions = db.Column(db.String(100))
    num_critical_messages = db.Column(db.Integer)

    comments = db.Column(db.Text)
    additional_info = db.Column(db.String(500))

    def __repr__(self):
        return f"<ChatSessionSummary {self.session_id}>"


 ##########################################
         
# Orders model
class Delivery(db.Model):
    __tablename__ = 'Delivery'  # Ensure this matches the table name in the database

    id = db.Column(db.Integer, primary_key=True)  # Primary key for the Delivery table
    #user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key linking to User
    user_id = db.Column(
    db.Integer,
    db.ForeignKey('user.id', name='fk_user_delivery'),
    nullable=False
    )

    order_id = db.Column(db.String(100), nullable=False, unique=True)
    status = db.Column(db.String(50), nullable=False)
    purchase_date = db.Column(db.DateTime)
    shipped_date = db.Column(db.DateTime)
    delivery_date = db.Column(db.DateTime)
    estimated_time = db.Column(db.String(50))  # Adding this column if needed

    user = db.relationship('User', back_populates='deliveries')

    def __repr__(self):
        return f"<Delivery {self.id}, {self.status}>"


##########################################

# Products model
class Product(db.Model):
    __tablename__ = 'Products'  # Ensure this matches the table name in the database
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specifications = db.Column(db.String(1028), nullable=False)
    release_date = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    additional_information = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<Product {self.product_name}>'


##########################################
    
# Services model
class Service(db.Model):
    __tablename__ = 'Services'  # Ensure this matches the table name in the database
    
    id = db.Column(db.Integer, primary_key=True)
    service_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(512), nullable=False)
    additional_information = db.Column(db.String(255), nullable=True)
    availability = db.Column(db.String(100), nullable=False)
    additional_info = db.Column(db.String(255), nullable=True)


    def __repr__(self):
        return f'<Service {self.service_type}>'

##########################################