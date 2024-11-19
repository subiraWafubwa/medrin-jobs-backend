from uuid import UUID
from flask import Blueprint, request, jsonify
from models import ApplicationStatusEnum, db, Application, JobSeeker, Job, shortlisted_applications
from config import send_email

application_bp = Blueprint('application', __name__)

@application_bp.route('/get_applicants/<job_id>', methods=['GET'])
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
    
@application_bp.route('/apply_job', methods=['POST'])
def apply_for_job():
    try:
        data = request.get_json()

        # Extract and validate required fields
        jobseeker_id = data.get('jobseeker_id')
        job_id = data.get('job_id')

        if not jobseeker_id or not job_id:
            return jsonify({"error": "Jobseeker ID and Job ID are required"}), 400

        try:
            # Convert strings to UUIDs
            jobseeker_id = UUID(jobseeker_id)
            job_id = UUID(job_id)
        except ValueError:
            return jsonify({"error": "Invalid UUID format for Jobseeker ID or Job ID"}), 400

        # Check for an existing application
        existing_application = Application.query.filter_by(
            jobseeker_id=jobseeker_id,
            job_id=job_id
        ).first()

        if existing_application:
            return jsonify({"error": "You have already applied for this job"}), 400

        # Create a new application
        application = Application(
            jobseeker_id=jobseeker_id,
            job_id=job_id,
            status=ApplicationStatusEnum.pending
        )

        db.session.add(application)
        db.session.commit()

        return jsonify({
            "message": "Application submitted successfully",
            "application_id": str(application.id),
            "status": application.status.name
        }), 201

    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@application_bp.route('/approve_applicant/<application_id>', methods=['PATCH'])
def approve_applicant(application_id):
    try:
        # Validate application_id format
        try:
            application_id = UUID(application_id)
        except ValueError:
            return jsonify({"error": "Invalid application ID format"}), 400

        # Fetch the application by ID
        application = Application.query.filter_by(id=application_id).first()
        if not application:
            return jsonify({"error": "No application found for the specified JobSeeker"}), 404

        # Update the application status to approved
        application.status = ApplicationStatusEnum.approved
        db.session.commit()

        # Fetch the jobseeker using the jobseeker_id from the application
        jobseeker = JobSeeker.query.filter_by(id=application.jobseeker_id).first()
        if not jobseeker:
            return jsonify({"error": "Application not found"}), 404

        # Fetch the user's email from the jobseeker
        email = jobseeker.user.email

        # Send approval email
        send_email(
            subject="Application Approved",
            email=email,
            body=f"Dear {jobseeker.first_name} {jobseeker.last_name},\n\n"
                 f"Congratulations! Your application for the job has been approved. "
                 f"We look forward to seeing what you will achieve in this role.\n\n"
                 f"Best regards,\nYour Team"
        )

        return jsonify({"message": "Application approved, and email notification sent successfully."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@application_bp.route('/reject_applicant/<application_id>', methods=['PATCH'])
def reject_applicant(application_id):
    try:
        try:
            application_id = UUID(application_id)
        except ValueError:
            return jsonify({"error": "Invalid application ID format"}), 400

        application = Application.query.filter_by(id=application_id).first()
        if not application:
            return jsonify({"error": "No application found for the specified JobSeeker"}), 404
        
        job = Job.query.filter_by(id=application.job_id).first()
        if not job:
            return jsonify({"error": "Job associated with this application not found"}), 404

        application.status = ApplicationStatusEnum.rejected
        db.session.commit()

        jobseeker = JobSeeker.query.filter_by(id=application.jobseeker_id).first()
        if not jobseeker:
            return jsonify({"error": "Applicant not found"}), 404

        email = jobseeker.user.email

        send_email(
            subject="Application Rejected",
            email=email,
            body=f"Dear {jobseeker.first_name} {jobseeker.last_name},\n\n"
                f"Your application for the position of {job.title} has been reviewed, and unfortunately, "
                f"we have decided to move forward with other candidates.\n\n"
                f"Thank you for your interest and wishing you all the best.\n\n"
                f"Regards,\nYour Team"
        )

        return jsonify({"message": "Application rejected, and email notification sent successfully."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@application_bp.route('/shortlist_applications/<job_id>', methods=['POST'])
def shortlist_applications(job_id):
    try:
        try:
            job_id = UUID(job_id)
        except ValueError:
            return jsonify({"error": "Invalid job ID format"}), 400

        job = Job.query.filter_by(id=job_id).first()
        if not job:
            return jsonify({"error": "Job not found."}), 404

        applications = Application.query.filter_by(job_id=job_id).all()
        if not applications:
            return jsonify({"error": "No applications found for this job."}), 404

        shortlisted_ids = []
        for application in applications:
            if application.status == ApplicationStatusEnum.approved:
                db.session.execute(shortlisted_applications.insert().values(
                    job_id=job.id,
                    application_id=application.id
                ))
                shortlisted_ids.append(application.id)
            elif application.status == ApplicationStatusEnum.pending:
                application.status = ApplicationStatusEnum.rejected
                db.session.commit()

                jobseeker = JobSeeker.query.filter_by(id=application.jobseeker_id).first()
                if jobseeker:
                    send_email(
                        subject="Application Rejected",
                        email=jobseeker.user.email,
                        body=f"Dear {jobseeker.first_name} {jobseeker.last_name},\n\n"
                             f"Your application for {job.title} has been reviewed, and unfortunately, "
                             f"we have decided to move forward with other candidates.\n\n"
                             f"Thank you for your interest and wishing you all the best.\n\n"
                             f"Regards,\nYour Team"
                    )

        # Commit all changes
        db.session.commit()

        # Send a response with shortlisted application IDs
        return jsonify({
            "message": "Applications processed successfully.",
            "shortlisted_applications": shortlisted_ids
        }), 200

    except Exception as e:
        db.session.rollback()  # Rollback in case of an error
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
