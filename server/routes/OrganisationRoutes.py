from uuid import UUID
import cloudinary
from flask import Blueprint, jsonify, request
from config import db
from models import Job, Organisation, User

organisation_bp = Blueprint('organisation', __name__)

@organisation_bp.route('/create_organisation', methods=['POST'])
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

    organisation = Organisation(
        user_id=user_id,
        name=name,
        location=location,
        description=description,
        mission=mission,
        vision=vision
    )

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



@organisation_bp.route('/update_organisation', methods=['PATCH'])
def update_organisation():
    data = request.form

    organisation_id = data.get('organisation_id')
    name = data.get('name')
    description = data.get('description')
    mission = data.get('mission')
    location = data.get('location')
    vision = data.get('vision')
    logo = request.files.get('logo')

    if not organisation_id:
        return jsonify({"error": "organisation_id is required"}), 400

    try:
        organisation_id = UUID(organisation_id)
    except ValueError:
        return jsonify({"error": "Invalid organisation_id format"}), 400

    organisation = Organisation.query.get(organisation_id)
    if not organisation:
        return jsonify({"error": "Organisation not found"}), 404

    # Update the fields
    if name:
        organisation.name = name
    if description:
        organisation.description = description
    if mission:
        organisation.mission = mission
    if vision:
        organisation.vision = vision
    if location:
        organisation.location = location

    # Upload the logo if provided
    if logo:
        try:
            organisation.logo = upload_logo(logo)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Save changes to the database
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error updating organisation: {e}")
        return jsonify({"error": "Failed to update organisation"}), 500

    return jsonify({
        "message": "Organisation updated successfully!",
        "organisation": {
            "id": str(organisation.id),
            "location": organisation.location,
            "name": organisation.name,
            "description": organisation.description,
            "mission": organisation.mission,
            "vision": organisation.vision,
            "logo": organisation.logo
        }
    }), 200

# Uploading a logo
def upload_logo(logo):
    try:
        upload_result = cloudinary.uploader.upload(
            logo,
            folder="organisations/logos"
        )
        return upload_result.get('secure_url')
    except Exception as e:
        print(f"Error uploading logo: {e}")
        raise Exception("Logo upload failed")

@organisation_bp.route('/get_jobs/<organisation_id>', methods=['GET'])
def get_jobs_for_organisation(organisation_id):
    try:
        try:
            organisation_id = UUID(organisation_id)
        except ValueError:
            return jsonify({"error": "Invalid organisation ID format"}), 400

        jobs = Job.query.filter_by(organisation_id=organisation_id).all()

        if not jobs:
            return jsonify({"message": "No jobs found for this organisation."}), 404

        return jsonify([job.to_dict() for job in jobs]), 200

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
