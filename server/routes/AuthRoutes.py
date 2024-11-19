import re
import pyotp
import bcrypt

from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import create_access_token, get_jwt, jwt_required
from config import BLACKLIST, db,  send_email
from models import User, RoleEnum
from datetime import datetime, timedelta

auth_bp = Blueprint('signup', __name__)

unverified_users = {}

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    email_validate_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')

    # Validate email
    if not email:
        return jsonify({"error": "Please add an email"}), 400
    
    if not re.match(email_validate_pattern, email):
        return jsonify({"error": "Invalid email format"}), 400
    
    # Validate password
    if not password:
        return jsonify({"error": "Please provide a password"}), 400
    
    if len(password) < 8:
        return jsonify({"error": "Password should be at least 8 characters"}), 400

    # Validate role
    if not role:
        return jsonify({"error": "Please select a role"}), 400

    if role not in RoleEnum._member_names_:
        return jsonify({"error": "Invalid role"}), 400

    # Check for existing user
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "A user with this email already exists"}), 400

    # Hash password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Generate OTP
    totp = pyotp.TOTP(pyotp.random_base32(), digits=6)
    otp = totp.now()

    print(otp)

    # Save user data temporarily
    unverified_users[email] = {
        "email": email,
        "password": hashed_password,
        "role": role,
        "otp": otp
    }

    # Send OTP email
    send_email(
        subject="Your OTP code", 
        email=email,
        body=f"Your OTP code is {otp}. It will expire in 5 minutes."
    )

    return jsonify({
        "message": "User registered successfully. OTP sent to email.",
        "otp": otp
    }), 200


@auth_bp.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get('email')
    otp_input = str(data.get('otp'))

    if email not in unverified_users:
        return jsonify({"error": "This user has not registered"}), 400

    user_data = unverified_users[email]
    otp = str(user_data['otp'])
    timestamp = datetime.now()

    # Check if OTP has expired (5 minutes)
    if datetime.now() - timestamp > timedelta(minutes=5):
        del unverified_users[email] 
        return jsonify({"error": "OTP has expired"}), 400

    if otp_input == otp:
        new_user = User(
            email=user_data['email'],
            password=user_data['password'],
            role=user_data['role'],
            timestamp=datetime.now()
        )
        db.session.add(new_user)
        db.session.commit()

        # Generate a JWT token
        access_token = create_access_token(identity=new_user.id)

        # Remove user from the unverified list
        del unverified_users[email]

        return jsonify({
            "message": "OTP verified successfully. User registered!",
            "user": {
                "id": str(new_user.id),
                "email": new_user.email,
                "role": new_user.role.name,
                "token": access_token
            }
        }), 200
    else:
        return jsonify({"error": "Invalid OTP"}), 400
    
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"error": "Invalid email"}), 401

    # Verify the password using bcrypt
    if not bcrypt.checkpw(password.encode('utf-8'), user.password):
        print("Password verification failed.")
        return jsonify({"error": "Incorrect password"}), 401

    # Generate access token for the user
    access_token = create_access_token(identity=email)

    return jsonify({
        "message": "Login successful!",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "role": user.role.name,
            "token": access_token
        }
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        jti = get_jwt()["jti"]

        BLACKLIST.add(jti)
        session.clear()

        return jsonify({"message": "Logout successful, token has been revoked."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500