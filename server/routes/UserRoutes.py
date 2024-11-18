from flask import Blueprint, jsonify
from middlewares.auth import token_required

get_data_bp = Blueprint('getdata', __name__)

@get_data_bp.route('/user', methods=['GET'])
@token_required
def get_user_data(user):
    try:
        return jsonify({
            "user": user.to_dict()
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

