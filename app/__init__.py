import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from logging.handlers import TimedRotatingFileHandler, SMTPHandler
from datetime import datetime
import logging
from flask import has_request_context, request
from flask_login import current_user

from app.config import Config

# === Initialize extensions ===
db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'


class UserContextFilter(logging.Filter):
    def filter(self, record):
        if has_request_context() and current_user.is_authenticated:
            record.user_id = current_user.get_id()
            record.user_email = current_user.email
        else:
            record.user_id = "-"
            record.user_email = "-"
        return True

def create_app():
    app = Flask(__name__)
    
    # === Configuration ===
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config.from_object(Config)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(app.instance_path, "site.db")}'
    app.config["WTF_CSRF_ENABLED"] = False

    # === Initialize extensions with app ===
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf = CSRFProtect(app)

    # === Logging setup ===
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    log_filename = "sentana.log"
    log_path = os.path.join(log_dir, log_filename)
    open(log_path, 'w').close()  # Clear old logs on startup

    formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - [User %(user_id)s | %(user_email)s] - %(name)s - %(funcName)s - line %(lineno)d - %(message)s')


    file_handler = TimedRotatingFileHandler(
        log_path, when="midnight", interval=1, backupCount=30, encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    user_filter = UserContextFilter()

    file_handler.addFilter(user_filter)
    

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(user_filter)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Avoid duplicate handlers in dev reloads
    if not any(isinstance(h, TimedRotatingFileHandler) for h in logger.handlers):
        logger.addHandler(file_handler)
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        logger.addHandler(console_handler)

    logger.info("\n\n✅ Logging with rotation initialized in __init__.py \n\n")

    # === Email alert handler (production only) ===

    from dotenv import load_dotenv
    load_dotenv()

    EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")         # e.g. your_gmail@gmail.com
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD") # the 16-char app password

    from app.logging_utils import CustomEmailHandler

    if not app.debug and os.environ.get("FLASK_ENV") == "production":
    # configure email alert handler
        mail_handler = CustomEmailHandler(
            mailhost=("smtp.gmail.com", 587),
            fromaddr=EMAIL_HOST_USER,
            toaddrs=["your_alert_email@example.com"],
            subject="🚨 SentAna Admin Alert",
            credentials=(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD),
            secure=()
        )
        mail_handler.setLevel(logging.ERROR)
        mail_handler.setFormatter(formatter)
        mail_handler.addFilter(user_filter)
        logger.addHandler(mail_handler)


    # === Register blueprints ===
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # === User loader for Flask-Login ===
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # === Ensure DB tables are created ===
    with app.app_context():
        from app import routes, models  # Avoid circular imports
        db.create_all()

    return app
