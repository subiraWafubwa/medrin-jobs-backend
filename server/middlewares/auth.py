from functools import wraps
from config import BLACKLIST, jwt
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models import User

# Middleware for token requirement
def token_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Verify the JWT token from the 'Authorization' header
            verify_jwt_in_request()
            
            # Get user email (or other identity info) from the token
            user_email = get_jwt_identity()

            # Retrieve user from the database using the email extracted from the token
            user = User.query.filter_by(email=user_email).first()
            if not user:
                return jsonify({"msg": "User not found"}), 404

            # Pass the user to the view function
            kwargs['user'] = user
            return func(*args, **kwargs)
        except Exception as err:
            return jsonify({"error": str(err)}), 500
    return wrapper

@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    return jwt_payload["jti"] in BLACKLIST
