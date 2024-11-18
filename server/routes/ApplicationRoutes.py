from uuid import UUID
from flask import Blueprint, request, jsonify
from models import ApplicationStatusEnum, db, Application, JobSeeker, Job
from datetime import datetime

application_bp = Blueprint('application', __name__)

@application_bp.route('/jobs/<job_id>/applicants', methods=['GET'])
def get_applicants_for_job(job_id):
    try:
        # Validate job_id as a UUID
        try:
            job_id = UUID(job_id)
        except ValueError:
            return jsonify({"error": "Invalid job ID format"}), 400

        # Check if the job exists
        job = Job.query.filter_by(id=job_id).first()
        if not job:
            return jsonify({"error": "Job not found"}), 404

        # Get all applications for the job
        applications = (
            Application.query
            .filter_by(job_id=job_id)
            .join(JobSeeker, Application.jobseeker_id == JobSeeker.id)
            .all()
        )

        # Structure the response
        applicants = [
            {
                "first_name": app.first_name,
                "last_name": app.last_name,
                "location": app.location,
                "phone": app.phone,
                "cv": app.cv,
                "application_date": app.timestamp.isoformat(),
                "status": app.status.name
            }
            for app in applications
        ]

        return jsonify({
            "job_id": str(job.id),
            "title": job.title,
            "applicants": applicants
        }), 200

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
