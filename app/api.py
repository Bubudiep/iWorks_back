# app/api.py

from flask import Blueprint, request, jsonify
from app.models import User
from app import db
import jwt
from functools import wraps
from app.config import Config  # Nhập Config thay vì JWT_SECRET_KEY trực tiếp
from . import models

api = Blueprint('api', __name__)

def init_app(app):
    @app.route("/")
    def index():
        return "API is running!"

    @app.route('/register', methods=['POST'])
    def register():
        data = request.get_json()
        # Implement registration logic
        return jsonify({'message': 'User registered'}), 201

    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        # Implement login logic and return access token
        return jsonify({'token': 'your_token_here'}), 200

    @app.route('/profile/<int:user_id>', methods=['GET'])
    def get_profile(user_id):
        profile = Profile.query.filter_by(user_id=user_id).first()
        if profile:
            return jsonify(ProfileSchema().dump(profile))
        return jsonify({'message': 'Profile not found'}), 404

    @app.route('/time_logs/<int:user_id>', methods=['GET'])
    def get_time_logs(user_id):
        time_logs = TimeLog.query.filter_by(user_id=user_id).all()
        return jsonify(TimeLogSchema(many=True).dump(time_logs))

    @app.route("/user/", methods=['GET'])
    def get_user():
        user_id = request.args.get('id')
        if user_id:
            # Thực hiện xử lý với user_id
            user_info = {
                "user_id": user_id,
                "name": "John Doe",
                "email": "john.doe@example.com"
            }
            return jsonify(user_info)
        else:
            return jsonify({"error": "ID parameter is missing"}), 400

    @api.route('/secure-data', methods=['GET'])
    @token_required
    def get_secure_data():
        # Implement secure data retrieval
        return jsonify({'data': 'This is secured data'})

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        try:
            jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
        except:
            return jsonify({'message': 'Token is invalid!'}), 403
        return f(*args, **kwargs)
    return decorated_function
