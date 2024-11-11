from flask import Blueprint, request, jsonify, session
from flask_mail import Message
from datetime import datetime
from flask_jwt_extended import create_access_token, get_jwt, jwt_required
import pyotp
import time
from config import BLACKLIST, db, mail, bcrypt
from models import Employer, User, RoleEnum, JobSeeker

auth_bp = Blueprint('signup', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    # Get data from POST method
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')

    if not email or not password or not role:
        return jsonify({"error": "Email, password, and role are required"}), 400

    if role not in RoleEnum._member_names_:
        return jsonify({"error": "Invalid role"}), 400

    # Check if a user with the same email already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "A user with this email already exists"}), 400

    # Generate and store OTP
    totp = pyotp.TOTP(pyotp.random_base32(), digits=6)  # 6-digit OTP
    otp = totp.now()

    # Store data inside session
    session['email'] = email
    session['otp'] = otp
    session['timestamp'] = time.time()
    session['password'] = password
    session['role'] = role

    # Send OTP email
    msg = Message("Your OTP Code", recipients=[email])
    msg.body = f"Your OTP code is {otp}. It will expire in 5 minutes."
    mail.send(msg)

    print(session['otp'])

    return jsonify({"message": "User registered successfully. OTP sent to email."}), 200


@auth_bp.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get('email')
    otp_input = data.get('otp')

    # Check if OTP exists and has not expired
    if 'email' not in session or session['email'] != email:
        return jsonify({"error": "No OTP generated for this email"}), 400

    otp = session['otp']
    timestamp = session['timestamp']
    password = session['password']
    role = session['role']

    # Check if OTP has expired (5 minutes)
    if time.time() - timestamp > 300:  # 5 minutes = 300 seconds
        return jsonify({"error": "OTP has expired"}), 400

    # Validate OTP
    if otp_input == otp:
        # OTP is valid, create new user
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(
            email=email,
            password=hashed_password,
            role=role
        )

        # Generate JWT token
        access_token = create_access_token(identity=email)

        # Save user to database
        db.session.add(user)
        db.session.commit()

        # Saving the id for JobSeeker and Employer post routes
        session['user_id'] = user.id

        return jsonify({
            "message": "User created successfully!",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "role": user.role.name,
                "token": access_token
            }
        }), 201

    else:
        return jsonify({"error": "Invalid OTP"}), 400
    
@auth_bp.route('/create_jobseeker', methods=['POST'])
def create_jobseeker():
    user_id = session.get('user_id')

    # Check if user_id exists in the session (i.e., the user has signed up and verified OTP)
    if not user_id:
        return jsonify({"error": "User must be registered and logged in to create a JobSeeker profile"}), 400

    # Get data from POST request
    data = request.get_json()

    first_name = data.get('first_name')
    last_name = data.get('last_name')
    location = data.get('location')
    phone = data.get('phone')
    dob_str = data.get('dob')

    # Ensure that required fields are provided
    if not first_name or not last_name or not location or not phone or not dob_str:
        return jsonify({"error": "First name, last name, location, phone, and date of birth are required"}), 400
    
    # Convert dob string to datetime object
    try:
        dob = datetime.strptime(dob_str, '%d/%m/%Y')
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use 'DD/MM/YYYY'"}), 400
    
    print(f"Parsed DOB: {dob}")

    # Create a new JobSeeker
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

@auth_bp.route('/create_employer', methods=['POST'])
def create_employer():
    user_id = session.get('user_id')
    print(user_id)

    # Get data from POST request
    data = request.get_json()
    name = data.get('name')
    location = data.get('location')
    description = data.get('description')
    mission = data.get('mission')
    vision = data.get('vision')

    # Check if all required fields are provided
    if not name or not location or not description or not mission or not vision:
        return jsonify({"error": "name, location, description, mission, and vision are required"}), 400

    # Validate the user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Create the Employer object
    employer = Employer(
        user_id=user_id,
        name=name,
        location=location,
        description=description,
        mission=mission,
        vision=vision
    )

    # Save the employer to the database
    db.session.add(employer)
    db.session.commit()

    # Clear session data
    session.clear()

    return jsonify({
        "message": "Employer profile created successfully!",
        "employer": {
            "id": str(employer.id),
            "user_id": str(employer.user_id),
            "name": employer.name,
            "location": employer.location,
            "description": employer.description,
            "mission": employer.mission,
            "vision": employer.vision
        }
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    email = data.get('email')
    password = data.get('password')
    
    # Check if email and password are provided
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    # Retrieve the user by email and password
    user = User.query.filter_by(email=email).first()
    
    if not user:
        return jsonify({"error": "Invalid email"}), 401
    
    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Incorrect password"}), 401
    
    # Generate JWT token
    access_token = create_access_token(identity=email)

    # Return the response with the JWT token
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
        # Get the token's unique identifier
        jti = get_jwt()["jti"]

        # Add the JTI to the blacklist
        BLACKLIST.add(jti)
        session.clear()

        return jsonify({"message": "Logout successful, token has been revoked."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500