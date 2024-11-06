from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

# Instantiate app, set configurations
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['JWT_SECRET_KEY'] = 'your_secret_key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 864000  # 10 days

# Define metadata for naming conventions
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

# Initialize extensions
db = SQLAlchemy(metadata=metadata)
migrate = Migrate()
api = Api()
cors = CORS()
bcrypt = Bcrypt()
jwt = JWTManager()

# Extension setup function
def init_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    api.init_app(app)
    cors.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
