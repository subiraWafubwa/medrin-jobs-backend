from uuid import UUID
from flask import Blueprint, request, jsonify
from models import Organisation, User, db, Application, JobSeeker, Job
from datetime import datetime
from config import send_email
from sqlalchemy.exc import SQLAlchemyError

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/all_jobs', methods=['GET'])
def get_all_jobs():
    try:
        jobs = Job.query.all()
        if not jobs:
            return jsonify({"message": "No jobs found."}), 404

        job_list = [job.to_dict() for job in jobs]
        return jsonify({"jobs": job_list}), 200
    except SQLAlchemyError as e:
        return jsonify({"error": "Failed to fetch jobs.", "details": str(e)}), 500


@admin_bp.route('/all_jobseekers', methods=['GET'])
def get_all_jobseekers():
    try:
        jobseekers = JobSeeker.query.all()
        if not jobseekers:
            return jsonify({"message": "No jobseekers found."}), 404

        jobseeker_list = [jobseeker.to_dict() for jobseeker in jobseekers]
        return jsonify({"jobseekers": jobseeker_list}), 200
    except SQLAlchemyError as e:
        return jsonify({"error": "Failed to fetch jobseekers.", "details": str(e)}), 500


@admin_bp.route('/all_organisations', methods=['GET'])
def get_all_organisations():
    try:
        organisations = Organisation.query.all()
        if not organisations:
            return jsonify({"message": "No organisations found."}), 404

        organisation_list = [organisation.to_dict() for organisation in organisations]
        return jsonify({"organisations": organisation_list}), 200
    except SQLAlchemyError as e:
        return jsonify({"error": "Failed to fetch organisations.", "details": str(e)}), 500


@admin_bp.route('/all_users', methods=['GET'])
def get_all_users():
    try:
        users = User.query.all()
        if not users:
            return jsonify({"message": "No users found."}), 404

        user_list = [user.to_dict() for user in users]
        return jsonify({"users": user_list}), 200
    except SQLAlchemyError as e:
        return jsonify({"error": "Failed to fetch users.", "details": str(e)}), 500


@admin_bp.route('/all_applications', methods=['GET'])
def get_all_applications():
    try:
        applications = Application.query.all()
        if not applications:
            return jsonify({"message": "No applications found."}), 404

        application_list = [application.to_dict() for application in applications]
        return jsonify({"applications": application_list}), 200
    except SQLAlchemyError as e:
        return jsonify({"error": "Failed to fetch applications.", "details": str(e)}), 500
