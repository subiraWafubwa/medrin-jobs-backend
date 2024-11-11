from flask import Blueprint, jsonify
from middlewares.auth import token_required
from models import User

get_data_bp = Blueprint('getdata', __name__)

@get_data_bp.route('/get_profile', methods=['GET'])
@token_required
def get_user_data(user):
    try:
        return jsonify({
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role.name if user.role else None,
                "employer_id": user.employer.id
            }
        }), 200

    except Exception as e:
        
        return jsonify({"error": str(e)}), 500
