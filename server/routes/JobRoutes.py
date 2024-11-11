from flask import Blueprint, request, jsonify
from datetime import datetime
from models import Job, Employer, JobRequirement, JobResponsibility, JobTypeEnum, JobLevelEnum, IndustryEnum, db

job_bp = Blueprint('job', __name__)

@job_bp.route('/add_job/<uuid:employer_id>', methods=['POST'])
def add_job(employer_id):
    # Ensure that the employer exists
    employer = Employer.query.get(employer_id)
    if not employer:
        return jsonify({"error": "Employer not found"}), 404
    
    # Get data from POST request
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    industry = data.get('industry')
    level = data.get('level')
    job_type = data.get('job_type')

    # Validate required fields
    if not title or not description or not industry or not level or not job_type:
        return jsonify({"error": "All fields are required: title, description, industry, level, job_type"}), 400

    # Ensure valid enum values
    if industry not in IndustryEnum._member_names_:
        return jsonify({"error": "Invalid industry value"}), 400
    if level not in JobLevelEnum._member_names_:
        return jsonify({"error": "Invalid job level value"}), 400
    if job_type not in JobTypeEnum._member_names_:
        return jsonify({"error": "Invalid job type value"}), 400

    # Create the new Job object
    job = Job(
        employer_id=employer_id,
        industry=IndustryEnum[industry].value,
        title=title,
        description=description,
        level=JobLevelEnum[level].value,
        job_type=JobTypeEnum[job_type].value,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        date_posted=datetime.now()
    )

    print(industry)

    # Save job to the database
    db.session.add(job)
    db.session.commit()

    # Serialize the job details, converting enum values to strings using the `.value` attribute
    job_data = {
        "id": str(job.id),
        "employer_id": str(job.employer_id),
        "title": job.title,
        "description": job.description,
        "level": job.level.value,
        "job_type": job.job_type.value,
        "date_posted": job.date_posted.isoformat()
    }

    return jsonify({
        "message": "Job posted successfully!",
        "job": job_data
    }), 201

@job_bp.route('/add_job_requirements/<uuid:job_id>', methods=['POST'])
def add_job_requirements(job_id):
    # Ensure that the job exists
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    
    # Get data from POST request
    data = request.get_json()
    requirements = data.get('requirements')

    # Validate required fields
    if not requirements:
        return jsonify({"error": "Requirements are required"}), 400
    
    # Delete existing job requirements for this job
    JobRequirement.query.filter_by(job_id=job_id).delete()

    # Create the new JobRequirement object
    job_requirement = JobRequirement(
        job_id=job_id,
        requirements=requirements
    )

    # Save job requirement to the database
    db.session.add(job_requirement)
    db.session.commit()

    # Serialize the job requirement details
    job_requirement_data = {
        "id": str(job_requirement.id),
        "job_id": str(job_requirement.job_id),
        "requirements": job_requirement.requirements
    }

    return jsonify({
        "message": "Job requirement added successfully!",
        "job_requirement": job_requirement_data
    }), 201

@job_bp.route('/add_job_responsibility/<uuid:job_id>', methods=['POST'])
def add_job_responsibility(job_id):
    # Ensure that the job exists
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    
    # Get data from POST request
    data = request.get_json()
    description = data.get('description')

    # Validate required fields
    if not description:
        return jsonify({"error": "Description is required"}), 400
    
    # Delete existing job responsibilities for this job
    JobResponsibility.query.filter_by(job_id=job_id).delete()

    # Create the new JobResponsibility object
    job_responsibility = JobResponsibility(
        job_id=job_id,
        description=description
    )

    # Save job responsibility to the database
    db.session.add(job_responsibility)
    db.session.commit()

    # Serialize the job responsibility details
    job_responsibility_data = {
        "id": str(job_responsibility.id),
        "job_id": str(job_responsibility.job_id),
        "description": job_responsibility.description
    }

    return jsonify({
        "message": "Job responsibility added successfully!",
        "job_responsibility": job_responsibility_data
    }), 201


