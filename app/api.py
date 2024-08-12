# app/api.py

from flask import Blueprint, request, jsonify
from app.models import User
from app import db
import jwt
from functools import wraps
from app.config import Config  # Nhập Config thay vì JWT_SECRET_KEY trực tiếp
from .models import *
from .schemas import *
import re
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from flask import request, jsonify

api = Blueprint('api', __name__)

class StandardPagesPagination:
    def __init__(self, page, per_page):
        self.page = page
        self.per_page = per_page

    def paginate_query(self, query):
        total_items = len(query)
        start = (self.page - 1) * self.per_page
        end = start + self.per_page
        items = query[start:end]

        total_pages = (total_items + self.per_page - 1) // self.per_page

        return {
            'total_items': total_items,
            'total_pages': total_pages,
            'current_page': self.page,
            'per_page': self.per_page,
            'items': items
        }
        
def init_app(app):
    @app.route("/")
    def index():
        return "API is running!"

    @app.route('/register', methods=['POST'])
    def register():
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400

        zalo_id = data.get("zalo_id")
        zalo_name = data.get("zalo_name")
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        if not zalo_id:
            return jsonify({"error": "Please input zalo_id"}), 400
        if not zalo_name:
            return jsonify({"error": "Please input zalo_name"}), 400
        if not username:
            return jsonify({"error": "Please input user name"}), 400
        if not email:
            return jsonify({"error": "Please input email"}), 400
        if not password:
            return jsonify({"error": "Please input password"}), 400
        if not is_valid_email(email):
            return jsonify({"error": "Invalid email format"}), 400
        if not is_valid_password(password):
            return jsonify({"error": "Password must be at least 4 characters"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already registered"}), 400

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        with db.session.begin_nested():
            new_user = User(username=username, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.flush()  # Ensure that the new_user ID is generated
            new_profile = Profile(user_id=new_user.id, zalo_id=zalo_id, zalo_name=zalo_name)
            db.session.add(new_profile)
            db.session.flush()  # Đảm bảo dữ liệu được ghi vào cơ sở dữ liệu
            
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201

    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Please provide both email and password"}), 400

        user = User.query.filter_by(email=email).first()

        if not user:
            return jsonify({"error": "Email not found"}), 400

        # Kiểm tra mật khẩu
        if not check_password_hash(user.password, password):
            return jsonify({"error": "Incorrect password"}), 400

        # Tạo thời gian hết hạn cho token là 1 tuần kể từ thời điểm hiện tại
        expiration_time = datetime.datetime.utcnow() + datetime.timedelta(weeks=1)

        # Tạo JWT token với thời gian hết hạn
        token = jwt.encode({
            'user_id': user.id,
            'exp': expiration_time
        }, Config.JWT_SECRET_KEY, algorithm='HS256')

        return jsonify({'token': token,'exp': expiration_time}), 200

    @app.route('/profile', methods=['GET'])
    @token_required
    def get_profile(user_id):
        try:
            profile = Profile.query.filter_by(user_id=user_id).first()
            if profile:
                return jsonify(ProfileSchema().dump(profile))
            return jsonify({'message': 'Profile not found'}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/time_logs', methods=['GET'])
    @token_required
    def get_time_logs(user_id):
        time_logs = TimeLog.query.filter_by(user_id=user_id).all()
        return jsonify(TimeLogSchema(many=True).dump(time_logs))

    @app.route("/user/", methods=['GET'])
    @token_required
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
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'message': 'Token is missing!'}), 403
        
        parts = auth_header.split()
        if parts[0].lower() != 'bearer' or len(parts) != 2:
            return jsonify({'message': 'Token is invalid!'}), 403
        
        token = parts[1]
        
        try:
            # Giải mã token và lấy user_id
            decoded_token = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get('user_id')
            if not user_id:
                return jsonify({"error": "Invalid token"}), 401
            print(user_id)
            request.user_id = user_id

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 403
        
        # Truyền user_id vào hàm được bảo vệ
        return f(user_id=user_id,*args, **kwargs)
    
    return decorated_function

def is_valid_email(email):
    """
    Validates an email address using regular expression.

    :param email: The email address to validate
    :return: True if the email is valid, False otherwise
    """
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None
    
def is_valid_password(password):
    """
    Validates a password to ensure it meets the required criteria.

    :param password: The password to validate
    :return: True if the password is valid, False otherwise
    """
    # Password should be at least 8 characters long
    if len(password) < 4:
        return False

    # # Password should have at least one uppercase letter
    # if not re.search(r'[A-Z]', password):
    #     return False

    # # Password should have at least one lowercase letter
    # if not re.search(r'[a-z]', password):
    #     return False

    # # Password should have at least one digit
    # if not re.search(r'[0-9]', password):
    #     return False

    # # Password should have at least one special character
    # if not re.search(r'[\W_]', password):
    #     return False

    return True