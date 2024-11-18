from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_mail import Mail, Message

import cloudinary
import cloudinary.uploader
import cloudinary.api

# Instantiate app, set configurations
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['JWT_SECRET_KEY'] = 'your_secret_key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 864000  # 10 days

# Enable blacklisting for the JWTs
app.config["JWT_BLACKLIST_ENABLED"] = True
app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access"]

# File upload configuration
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'pdf', 'docx'}

# A set to store blacklisted tokens
BLACKLIST = set()

# Define metadata for naming conventions
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

# Email configurations
class MailConfig:
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USERNAME = 'wafubwacraig@gmail.com'
    MAIL_PASSWORD = 'mcudrlgjllqdphbw'
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    SECRET_KEY = 'your-secret-key'

app.config.from_object(MailConfig)

# Initialize extensions
db = SQLAlchemy(metadata=metadata)
migrate = Migrate()
api = Api()
cors = CORS()
bcrypt = Bcrypt()
jwt = JWTManager()
mail = Mail(app)

# Function to send emails
def send_email(subject, email, body):
    msg = Message(
        subject=subject,
        recipients=[email],
        sender=('Medrin Jobs', 'wafubwacraig@gmail.com')  # Proper sender format
    )
    msg.body = body
    mail.send(msg)

# Extension setup function
def init_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    api.init_app(app)
    cors.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

# Clouinary configuration
cloudinary.config(
    cloud_name='djmyqvyys',
    api_key='595518991534862',
    api_secret='DxFdZLzYt95SFntqA9yTLX7TVUk'
)
