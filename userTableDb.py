

# app/models.py
from app import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30), nullable=False)  # Added for new structure
    last_name = db.Column(db.String(30), nullable=False)   # Added for new structure
    username = db.Column(db.String(30), unique=True, nullable=False)  # Verify
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=True)  # Optional field
    company = db.Column(db.String(100), nullable=True)  # Optional field
    password_hash = db.Column(db.String(60), nullable=False)
    crm_contact_id = db.Column(db.String(255), nullable=True)  # CRM contact ID
    created_date = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
