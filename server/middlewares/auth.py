import jwt
from functools import wraps
from flask import request, jsonify
from config import app
from models import User

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]  # Extract token from header

        if not token:
            return jsonify({"error": "Token is missing!"}), 401

        try:
            # Decode token using your secret key
            data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
            user = User.query.filter_by(email=data['sub']).first()
            if not user:
                raise Exception("User not found")
        except Exception as e:
            return jsonify({"error": "Invalid token", "message": str(e)}), 401

        return f(user, *args, **kwargs)
    return decorated_function
