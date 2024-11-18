from datetime import datetime
from uuid import UUID

import cloudinary
from config import db
from flask import Blueprint, jsonify, request, session
from models import Application, ApplicationStatusEnum, Job, JobSeeker

jobseeker_bp = Blueprint('jobseeker', __name__)

@jobseeker_bp.route('/create_jobseeker', methods=['POST'])
def create_jobseeker():
    data = request.get_json()

    user_id = data.get('user_id')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    location = data.get('location')
    phone = data.get('phone')
    dob_str = data.get('dob')

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    if not first_name or not last_name or not location or not phone or not dob_str:
        return jsonify({"error": "First name, last name, location, phone, and date of birth are required"}), 400

    # Validate and convert user_id to UUID
    try:
        user_id = UUID(user_id)
    except ValueError:
        return jsonify({"error": "Invalid user ID format"}), 400

    # Validate and parse date of birth
    try:
        dob = datetime.strptime(dob_str, '%d/%m/%Y')
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use 'DD/MM/YYYY'"}), 400

    # Create JobSeeker object
    jobseeker = JobSeeker(
        user_id=user_id,
        first_name=first_name,
        last_name=last_name,
        location=location,
        phone=phone,
        dob=dob
    )

    try:
        # Save the jobseeker profile to the database
        db.session.add(jobseeker)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create JobSeeker profile: {str(e)}"}), 500

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
            "dob": jobseeker.dob.isoformat(),
            "cv": jobseeker.cv
        }
    }), 201

def upload_cv(file):
    try:
        upload_result = cloudinary.uploader.upload(
            file,
            folder="jobseekers/cvs",
            resource_type="raw"
        )
        return upload_result
    except Exception as e:
        print(f"Error uploading CV: {e}")
        raise


@jobseeker_bp.route('/update_jobseeker', methods=['PATCH'])
def update_jobseeker():
    data = request.form

    jobseeker_id = data.get('jobseeker_id')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    location = data.get('location')
    phone = data.get('phone')
    dob_str = data.get('dob')
    cv = request.files.get('cv')

    if not jobseeker_id:
        return jsonify({"error": "jobseeker_id is required"}), 400

    try:
        jobseeker_id = UUID(jobseeker_id)
    except ValueError:
        return jsonify({"error": "Invalid jobseeker_id format"}), 400

    jobseeker = JobSeeker.query.get(jobseeker_id)
    if not jobseeker:
        return jsonify({"error": "JobSeeker not found"}), 404

    # Update fields if provided
    if first_name:
        jobseeker.first_name = first_name
    if last_name:
        jobseeker.last_name = last_name
    if location:
        jobseeker.location = location
    if phone:
        jobseeker.phone = phone
    if dob_str:
        try:
            jobseeker.dob = datetime.strptime(dob_str, '%d/%m/%Y')
        except ValueError:
            return jsonify({"error": "Invalid date format. Please use 'DD/MM/YYYY'"}), 400

    # Upload CV to Cloudinary if provided
    if cv:
        try:
            upload_result = upload_cv(cv)
            jobseeker.cv = upload_result.get('secure_url')
        except Exception as e:
            return jsonify({"error": f"CV upload failed: {str(e)}"}), 500

    # Save changes to the database
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error updating jobseeker: {e}")
        return jsonify({"error": "Failed to update jobseeker"}), 500

    return jsonify({
        "message": "JobSeeker updated successfully!",
        "jobseeker": {
            "id": str(jobseeker.id),
            "first_name": jobseeker.first_name,
            "last_name": jobseeker.last_name,
            "location": jobseeker.location,
            "phone": jobseeker.phone,
            "dob": jobseeker.dob.isoformat() if jobseeker.dob else None,
            "cv": jobseeker.cv
        }
    }), 200

@jobseeker_bp.route('/apply-job', methods=['POST'])
def apply_job():
    data = request.get_json()

    job_id = data.get('job_id')
    jobseeker_id = data.get('jobseeker_id')

    # Ensure job_id is a valid UUID, even if it is passed as a string without dashes
    if len(job_id) == 32:
        job_id = f"{job_id[:8]}-{job_id[8:12]}-{job_id[12:16]}-{job_id[16:20]}-{job_id[20:]}"  # Reformat to UUID string with dashes

    try:
        job_id = UUID(job_id)
    except ValueError:
        return jsonify({"error": "Invalid job_id format"}), 400

    if len(jobseeker_id) == 32:
        jobseeker_id = f"{jobseeker_id[:8]}-{jobseeker_id[8:12]}-{jobseeker_id[12:16]}-{jobseeker_id[16:20]}-{jobseeker_id[20:]}"  # Reformat to UUID string with dashes

    # Convert jobseeker_id to a UUID object
    try:
        jobseeker_id = UUID(jobseeker_id)
    except ValueError:
        return jsonify({"error": "Invalid jobseeker_id format"}), 400

    # Query jobseeker
    jobseeker = JobSeeker.query.get(jobseeker_id)

    if not jobseeker:
        return jsonify({"error": "Invalid job_applicant"}), 400

    # Query job with filter_by
    job = Job.query.filter_by(id=job_id).first()

    if not job:
        return jsonify({"error": "Invalid job_id"}), 400

    # Create the application record
    application = Application(
        job_id=job_id,
        jobseeker_id=jobseeker_id,
        status=ApplicationStatusEnum.pending,
        created_at=datetime.now()
    )

    db.session.add(application)
    db.session.commit()

    return jsonify({
        "message": "Application submitted successfully", 
        "job_id": job_id,
        "jobseeker_id": jobseeker_id
    }), 201