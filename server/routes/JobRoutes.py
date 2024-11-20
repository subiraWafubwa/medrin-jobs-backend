from flask import Blueprint, request, jsonify
from datetime import datetime
from models import Job, Organisation, JobRequirement, JobResponsibility, JobTypeEnum, JobLevelEnum, IndustryEnum, JobBenefits, db, shortlisted_applications

job_bp = Blueprint('job', __name__)

@job_bp.route('/create_job/<uuid:organisation_id>', methods=['POST'])
def create_job(organisation_id):
    organisation = Organisation.query.get(organisation_id)
    if not organisation:
        return jsonify({"error": "Organisation not found"}), 404

    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    industry = data.get('industry')
    level = data.get('level')
    job_type = data.get('job_type')
    benefits_list = data.get('job_benefits')
    requirements_list = data.get('job_requirements', [])
    responsibilities_list = data.get('job_responsibilities', [])

    if not title or not description or not industry or not level or not job_type:
        return jsonify({"error": "All fields are required: title, description, industry, level, job_type"}), 400

    if industry not in IndustryEnum._member_names_:
        return jsonify({"error": "Invalid industry value"}), 400
    if level not in JobLevelEnum._member_names_:
        return jsonify({"error": "Invalid job level value"}), 400
    if job_type not in JobTypeEnum._member_names_:
        return jsonify({"error": "Invalid job type value"}), 400

    job = Job(
        organisation_id=organisation_id,
        industry=IndustryEnum[industry].value,
        title=title,
        description=description,
        level=JobLevelEnum[level].value,
        job_type=JobTypeEnum[job_type].value,
        timestamp=datetime.now()
    )

    db.session.add(job)
    db.session.commit()

    for requirement in requirements_list:
        job_requirement = JobRequirement(job_id=job.id, requirements=requirement)
        db.session.add(job_requirement)

    for responsibility in responsibilities_list:
        job_responsibility = JobResponsibility(job_id=job.id, description=responsibility)
        db.session.add(job_responsibility)

    for benefit in benefits_list:
        job_benefit = JobBenefits(job_id=job.id, description=benefit)
        db.session.add(job_benefit)

    db.session.commit()

    job_data = {
        "id": str(job.id),
        "organisation_id": str(job.organisation_id),
        "title": job.title,
        "description": job.description,
        "level": job.level.value,
        "job_type": job.job_type.value,
        "timestamp": job.timestamp.isoformat(),
        "job_requirements": [req.requirements for req in job.job_requirements],
        "job_responsibilities": [resp.description for resp in job.job_responsibilities]
    }

    return jsonify({
        "message": "Job posted successfully!",
        "job": job_data
    }), 201

@job_bp.route('/applicable_jobs', methods=['GET'])
def get_applicable_jobs():
    shortlisted_job_ids = db.session.query(shortlisted_applications.c.job_id).distinct()
    jobs = Job.query.filter(~Job.id.in_(shortlisted_job_ids)).all()

    job_list = [job.to_dict() for job in jobs]

    return jsonify({
        "applicable_jobs": job_list
    }), 200

@job_bp.route('/job/<uuid:job_id>', methods=['GET'])
def get_job_by_id(job_id):

    job = Job.query.get(job_id)
    
    if job is None:
        return jsonify({"error": "Job not found"}), 404

    return jsonify({"job": job.to_dict()}), 200


@job_bp.route('/jobs', methods=['GET'])
def get_jobs():

    jobs=[job.to_dict() for job in Job.query.all()] 
    
    if jobs is None:
        return jsonify({"error": "Jobs are not found"}), 404

    return jsonify(jobs), 200

@job_bp.route('/job/<uuid:job_id>', methods=['DELETE'])
def delete_job_by_id(job_id):

    job = Job.query.get(job_id)
    
    if job is None:
        return jsonify({"error": "Job not found"}), 404

    db.session.delete(job)
    db.session.commit()
    
    return jsonify({"message":"Job has been deleted successfully"}), 200

