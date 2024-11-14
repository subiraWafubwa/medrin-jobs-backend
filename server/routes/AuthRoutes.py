from flask import Blueprint, request, jsonify, session
from flask_mail import Message
from datetime import datetime
from flask_jwt_extended import create_access_token, get_jwt, jwt_required
import pyotp
from config import BLACKLIST, db, mail, bcrypt
from models import Organisation, User, RoleEnum, JobSeeker
from datetime import datetime
from flask import jsonify, request, session
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token
from datetime import timedelta
from uuid import UUID

bcrypt = Bcrypt()
auth_bp = Blueprint('signup', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')

    if not email or not password or not role:
        return jsonify({"error": "Email, password, and role are required"}), 400

    if role not in RoleEnum._member_names_:
        return jsonify({"error": "Invalid role"}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "A user with this email already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Generate and store OTP
    totp = pyotp.TOTP(pyotp.random_base32(), digits=6)
    otp = totp.now()

    new_user = User(
        email=email,
        password=hashed_password,
        role=role,
        otp=otp,
        timestamp=datetime.now()  
    )

    db.session.add(new_user)
    db.session.commit()

    # Send OTP email
    msg = Message("Your OTP Code", recipients=[email])
    msg.body = f"Your OTP code is {otp}. It will expire in 5 minutes."
    mail.send(msg)

    print("OTP sent:", otp)

    return jsonify({
        "message": "User registered successfully. OTP sent to email.",
        "otp": otp
    }), 200

@auth_bp.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get('email')
    otp_input = str(data.get('otp'))

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"error": "User not found"}), 400

    otp = str(user.otp)
    timestamp = user.timestamp

    # Check if OTP has expired (5 minutes)
    if datetime.now() - timestamp > timedelta(minutes=5):
        return jsonify({"error": "OTP has expired"}), 400

    if otp_input == otp:
        hashed_password = bcrypt.generate_password_hash(user.password).decode('utf-8')  # Hash the password
        user.password = hashed_password
        user.otp = None
        user.timestamp = None

        db.session.commit()

        # Generate a JWT token for the user to log them in
        access_token = create_access_token(identity=user.id)

        return jsonify({
            "message": "OTP verified successfully. User logged in!",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "role": user.role.name,
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

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Incorrect password"}), 401

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

@auth_bp.route('/create_jobseeker', methods=['POST'])
def create_jobseeker():
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({"error": "User must be registered and logged in to create a JobSeeker profile"}), 400

    data = request.get_json()

    first_name = data.get('first_name')
    last_name = data.get('last_name')
    location = data.get('location')
    phone = data.get('phone')
    dob_str = data.get('dob')

    if not first_name or not last_name or not location or not phone or not dob_str:
        return jsonify({"error": "First name, last name, location, phone, and date of birth are required"}), 400

    try:
        dob = datetime.strptime(dob_str, '%d/%m/%Y')
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use 'DD/MM/YYYY'"}), 400

    jobseeker = JobSeeker(
        user_id=user_id,
        first_name=first_name,
        last_name=last_name,
        location=location,
        phone=phone,
        dob=dob
    )

    # Save the jobseeker profile to the database
    db.session.add(jobseeker)
    db.session.commit()

    # Clear session data
    session.clear()

    return jsonify({
        "message": "JobSeeker profile created successfully!",
        "jobseeker": {
            "id": str(jobseeker.id),
            "user_id": str(jobseeker.user_id),
            "first_name": jobseeker.first_name,
            "last_name": jobseeker.last_name,
            "location": jobseeker.location,
            "phone": jobseeker.phone,
            "dob": jobseeker.dob.isoformat()
        }
    }), 201

@auth_bp.route('/create_organisation', methods=['POST'])
def create_organisation():
    data = request.get_json()

    user_id = data.get('user_id')
    name = data.get('name')
    location = data.get('location')
    description = data.get('description')
    mission = data.get('mission')
    vision = data.get('vision')

    if not user_id or not name or not location or not description or not mission or not vision:
        return jsonify({"error": "user_id, name, location, description, mission, and vision are required"}), 400

    try:
        user_id = UUID(user_id)
    except ValueError:
        return jsonify({"error": "Invalid user_id format"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Create the Organisation object
    organisation = Organisation(
        user_id=user_id,
        name=name,
        location=location,
        description=description,
        mission=mission,
        vision=vision
    )

    # Save the organisation to the database
    try:
        db.session.add(organisation)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error saving organisation: {e}")
        return jsonify({"error": "Failed to create organisation profile"}), 500

    return jsonify({
        "message": "Organisation profile created successfully!",
        "organisation": {
            "id": str(organisation.id),
            "user_id": str(organisation.user_id),
            "name": organisation.name,
            "location": organisation.location,
            "description": organisation.description,
            "mission": organisation.mission,
            "vision": organisation.vision
        }
    }), 201

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