from uuid import UUID
from flask import Blueprint, request, jsonify
from models import ApplicationStatusEnum, db, Application, JobSeeker, Job
from datetime import datetime

application_bp = Blueprint('application', __name__)

@application_bp.route('/apply-job', methods=['POST'])
def apply_job():
    data = request.get_json()

    job_id = data.get('job_id')
    jobseeker_id = data.get('jobseeker_id')

    # Ensure job_id is a valid UUID, even if it is passed as a string without dashes
    if len(job_id) == 32:
        job_id = f"{job_id[:8]}-{job_id[8:12]}-{job_id[12:16]}-{job_id[16:20]}-{job_id[20:]}"  # Reformat to UUID string with dashes

    # Convert job_id to a UUID object
    try:
        job_id = UUID(job_id)
    except ValueError:
        return jsonify({"error": "Invalid job_id format"}), 400

    # Ensure jobseeker_id is a valid UUID, even if it is passed as a string without dashes
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