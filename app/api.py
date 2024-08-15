import random
import string
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
from datetime import datetime, date, timedelta
from flask import request, jsonify
from sqlalchemy import extract


api = Blueprint('api', __name__)

class StandardPagesPagination:
    def __init__(self, query, page, per_page):
        self.page = page
        self.per_page = per_page
        self.total = query.count()
        self.pages = self.total // self.per_page + (
            1 if self.total % self.per_page > 0 else 0
        )
        self.items = (
            query.offset((self.page - 1) * self.per_page).limit(self.per_page).all()
        )
        self.base_url = request.base_url

    def get_page_link(self, page):
        if page < 1 or page > self.pages:
            return None
        return f"{self.base_url}?page={page}&page_size={self.per_page}"

    def to_dict(self, schema):
        items = schema.dump(self.items)
        return {
            "page": self.page,
            "page_size": self.per_page,
            "count": self.total,
            "items": items,
            "next_page": (
                self.get_page_link(self.page + 1) if self.page < self.pages else None
            ),
            "previous_page": (
                self.get_page_link(self.page - 1) if self.page > 1 else None
            ),
        }
        
def init_app(app):
    def generate_random_password(length=12):
        # Define the characters to use for the password
        characters = string.ascii_letters + string.digits + string.punctuation
        
        # Use random.choices to pick characters from the pool
        password = ''.join(random.choices(characters, k=length))
        
        return password

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
        
        zalo_id = data.get("zalo_id")
        email = data.get("email")
        password = data.get("password")
        if zalo_id and len(zalo_id)>15:
            profile = Profile.query.filter_by(zalo_id=zalo_id).first()
            print(f"{profile}")
            if profile:
                user = profile.user  # Lấy user từ profile
            else:
                # create a new user
                zalo_info = data.get("info")
                password = generate_random_password(16)
                hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
                user = User(username=zalo_info.get("id"),password=hashed_password)
                db.session.add(user)
                db.session.commit()
                profile = Profile(user_id=user.id, 
                                  zalo_id=zalo_id,
                                  zalo_name=zalo_info.get("name",None),
                                  zalo_avatar=zalo_info.get("avatar",None)
                                )
                db.session.add(profile)
                db.session.commit()
        else:
            if not email or not password:
                return jsonify({"error": "Please provide both email and password"}), 400
            user = User.query.filter_by(email=email).first()
            if not user:
                return jsonify({"error": "Email not found"}), 400
            # Kiểm tra mật khẩu
            if not check_password_hash(user.password, password):
                return jsonify({"error": "Incorrect password"}), 400
        # Tạo thời gian hết hạn cho token là 1 tuần kể từ thời điểm hiện tại
        expiration_time = datetime.utcnow() + timedelta(weeks=1)

        # Tạo JWT token với thời gian hết hạn
        token = jwt.encode({
            'user_id': user.id,
            'exp': expiration_time
        }, Config.JWT_SECRET_KEY, algorithm='HS256')
        print(f"{token}")

        return jsonify({'token': f"{token}",'exp': expiration_time}), 200
    
    @app.route('/worksalary', methods=['GET','POST'])
    @token_required
    def worksalary(user_id):
        if request.method == "GET":
            return get_worksalary(user_id)
        elif request.method == "POST":
            return create_worksalary(user_id)
    def get_worksalary(user_id):
        try:
            qs_WorkSalary = WorkSalary.query.join(WorkSheet).filter(
                WorkSheet.user_id == user_id
            )
            
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            pagination = StandardPagesPagination(qs_WorkSalary, page, per_page)
            project_schema = WorkSalarySchema(many=True)
            paginated_data = pagination.to_dict(project_schema)
            return jsonify(paginated_data), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    def create_worksalary(user_id):
        data = request.get_json()
        worksheet=data.get('Worksheet',None)
        if worksheet is None:
            return jsonify({'error': 'Worksheet is required'}), 400
        else:
            # Đảm bảo worksheet là của user_id
            qs_worksheet=WorkSheet.query.filter_by(id=worksheet,user_id=user_id).count()
            if qs_worksheet==0:
                return jsonify({'error': 'Không tìm thấy dữ liệu!'}), 400
        SalaryName=data.get('SalaryName',None)
        if SalaryName is None or SalaryName=="":
            return jsonify({'error': 'Vui lòng nhập tên!'}), 400
        Salary=data.get('Salary',None)
        if Salary is None:
            return jsonify({'error': 'Tiền lương không được để trống!'}), 400
        qs_salary=WorkSalary.query.filter_by(worksheet_id=worksheet,SalaryName=SalaryName)
        if qs_salary.count()>0:
            return jsonify({'error': f"{SalaryName} đã tồn tại!"}), 400
        
        new_worksheet = WorkSalary(
            worksheet_id=worksheet,
            SalaryName=SalaryName,
            Salary=Salary
        )
        db.session.add(new_worksheet)
        db.session.commit()
        return jsonify(WorkSalarySchema().dump(new_worksheet)), 201
    
    @app.route('/worksalary/<int:id>', methods=['GET','PATCH','DELETE'])
    @token_required
    def worksalary_fk(user_id,id):
        if request.method == "GET":
            return get_worksalary_fk(user_id,id)
        elif request.method == "PATCH":
            return update_worksalary_fk(user_id,id)
        elif request.method == "DELETE":
            return delete_worksalary_fk(user_id, id)
    def get_worksalary_fk(user_id,id):
        worksalary = WorkSalary.query.join(WorkSheet).filter(
            WorkSheet.user_id == user_id,
            WorkSalary.id == id
        ).first()
        if not worksalary:
            return jsonify({'message': 'WorkSalary not found'}), 404
        return jsonify(WorkSheetSchema().dump(worksheet))
    def update_worksalary_fk(user_id,id):
        worksalary = WorkSalary.query.join(WorkSheet).filter(
            WorkSheet.user_id == user_id,
            WorkSalary.id == id
        ).first()
        if not worksalary:
            return jsonify({'message': 'WorkSalary not found'}), 404

        data = request.get_json()

        worksalary.SalaryName = data.get('SalaryName', worksalary.SalaryName)
        worksalary.Salary = data.get('Salary', worksalary.Salary)

        db.session.commit()
        return jsonify(WorkSalarySchema().dump(worksalary)), 200
    def delete_worksalary_fk(user_id, id):
        worksalary = WorkSalary.query.join(WorkSheet).filter(
            WorkSheet.user_id == user_id,
            WorkSalary.id == id
        ).first()
        if not worksalary:
            return jsonify({'message': 'WorkSalary not found'}), 404
        db.session.delete(worksalary)
        db.session.commit()
        return jsonify({'message': 'WorkSalary deleted successfully'}), 200
    
    @app.route('/worksheet_details/<int:id>', methods=['GET'])
    @token_required
    def worksheet_details(user_id, id=None):
        if request.method == "GET":
            if id is None:
                return jsonify({'error': 'Invalid request method or missing id'}), 400
            else:
                return get_worksheet_details_fk(user_id, id)
    def get_worksheet_details_fk(user_id, id):
        worksheet = WorkSheet.query.filter_by(id=id, user_id=user_id).first()
        if not worksheet:
            return jsonify({'message': 'WorkSheet not found'}), 404
        return jsonify(WorkSheetDetailsSchema().dump(worksheet))
    
    @app.route('/worksheet_record/<int:id>', methods=['GET'])
    @token_required
    def worksheet_record(user_id, id=None):
        if request.method == "GET":
            if id is None:
                return jsonify({'error': 'Invalid request method or missing id'}), 400
            else:
                return get_worksheet_record_fk(user_id, id)
    def get_worksheet_record_fk(user_id, id):
        worksheet = WorkSheet.query.filter_by(id=id, user_id=user_id).first()
        if not worksheet:
            return jsonify({'message': 'WorkSheet not found'}), 404
        return jsonify(WorkSheetRecordSchema().dump(worksheet))
    
    @app.route('/worksheet_salary/<int:id>', methods=['GET'])
    @token_required
    def worksheet_salary(user_id, id=None):
        if request.method == "GET":
            if id is None:
                return jsonify({'error': 'Invalid request method or missing id'}), 400
            else:
                return get_worksheet_salary_fk(user_id, id)
    def get_worksheet_salary_fk(user_id, id):
        worksheet = WorkSheet.query.filter_by(id=id, user_id=user_id).first()
        if not worksheet:
            return jsonify({'message': 'WorkSheet not found'}), 404
        return jsonify(WorkSheetSalarySchema().dump(worksheet))
    
    @app.route('/worksheet', methods=['GET', 'POST', 'PATCH', 'DELETE'])
    @app.route('/worksheet/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
    @token_required
    def worksheet(user_id, id=None):
        if request.method == "GET":
            if id is None:
                return get_worksheet(user_id)
            else:
                return get_worksheet_fk(user_id, id)
        elif request.method == "POST" and id is None:
            return create_worksheet(user_id)
        elif request.method == "PATCH" and id is not None:
            return update_worksheet_fk(user_id, id)
        elif request.method == "DELETE" and id is not None:
            return delete_worksheet_fk(user_id, id)
        else:
            return jsonify({'error': 'Invalid request method or missing id'}), 400

    def get_worksheet(user_id):
        try:
            qs_worksheet = WorkSheet.query.filter_by(user_id=user_id)
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            pagination = StandardPagesPagination(qs_worksheet, page, per_page)
            project_schema = WorkSheetSchema(many=True)
            paginated_data = pagination.to_dict(project_schema)
            return jsonify(paginated_data), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def create_worksheet(user_id):
        data = request.get_json()
        company = data.get('Company', None)
        if company is None or company == "":
            return jsonify({'error': 'Bao gồm tên công ty'}), 400
        qs_company = WorkSheet.query.filter_by(user_id=user_id, Company=company)
        if qs_company.count() > 0:
            return jsonify({'error': 'Công ty này đã có'}), 400
        new_worksheet = WorkSheet(
            user_id=user_id,
            Company=company,
            isActive=True
        )
        db.session.add(new_worksheet)
        db.session.commit()
        return jsonify(WorkSheetSchema().dump(new_worksheet)), 201

    def get_worksheet_fk(user_id, id):
        worksheet = WorkSheet.query.filter_by(id=id, user_id=user_id).first()
        if not worksheet:
            return jsonify({'message': 'WorkSheet not found'}), 404
        return jsonify(WorkSheetSchema().dump(worksheet))

    def update_worksheet_fk(user_id, id):
        worksheet = WorkSheet.query.filter_by(id=id, user_id=user_id).first()
        if not worksheet:
            return jsonify({'message': 'WorkSheet not found'}), 404

        data = request.get_json()

        worksheet.Company = data.get('Company', worksheet.Company)
        worksheet.isActive = data.get('isActive', worksheet.isActive)

        db.session.commit()
        return jsonify(WorkSheetSchema().dump(worksheet)), 200

    def delete_worksheet_fk(user_id, id):
        worksheet = WorkSheet.query.filter_by(id=id, user_id=user_id).first()
        if not worksheet:
            return jsonify({'message': 'WorkSheet not found'}), 404
        db.session.delete(worksheet)
        db.session.commit()
        return jsonify({'message': 'WorkSheet deleted successfully'}), 200


    @app.route('/workrecord', methods=['GET', 'POST', 'PATCH', 'DELETE'])
    @app.route('/workrecord/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
    @token_required
    def workrecord(user_id, id=None):
        if request.method == "GET":
            if id is None:
                return get_workrecord(user_id)
            else:
                return get_workrecord_fk(user_id, id)
        elif request.method == "POST" and id is None:
            return create_workrecord(user_id)
        elif request.method == "PATCH" and id is not None:
            return update_workrecord_fk(user_id, id)
        elif request.method == "DELETE" and id is not None:
            return delete_workrecord_fk(user_id, id)
        else:
            return jsonify({'error': 'Invalid request method or missing id'}), 400

    def get_workrecord(user_id):
        try:
            qs_workrecord = WorkRecord.query.join(WorkSheet).filter(WorkSheet.user_id == user_id)
            worksheet = request.args.get('worksheet',None)
            if worksheet is not None:
                qs_workrecord = qs_workrecord.filter(WorkRecord.worksheet_id==worksheet)

            month = request.args.get('month', None, type=int)
            year = request.args.get('year', None, type=int)
            if month is not None and year is not None:
                qs_workrecord = qs_workrecord.filter(
                    extract('month', WorkRecord.workDate) == month,
                    extract('year', WorkRecord.workDate) == year
                )
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            pagination = StandardPagesPagination(qs_workrecord, page, per_page)
            workrecord_schema = WorkRecordSchema(many=True)
            paginated_data = pagination.to_dict(workrecord_schema)
            return jsonify(paginated_data), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def create_workrecord(user_id):
        data = request.get_json()
        worksheet_id = data.get('worksheet_id', None)
        workDate_str = data.get('workDate', None)
        startTime_str = data.get('startTime', None)
        endTime_str = data.get('endTime', None)
        overTime = data.get('overTime', None)
        lateTime = data.get('lateTime', None)
        # Convert string to date or datetime objects
        workDate = datetime.strptime(workDate_str, '%Y-%m-%d').date() if workDate_str else None
        startTime = datetime.strptime(startTime_str, '%Y-%m-%d %H:%M:%S') if startTime_str else None
        endTime = datetime.strptime(endTime_str, '%Y-%m-%d %H:%M:%S') if endTime_str else None

        if not worksheet_id or not WorkSheet.query.filter_by(id=worksheet_id, user_id=user_id).first():
            return jsonify({'error': 'Invalid worksheet ID or worksheet does not belong to user'}), 400
        qs_workrecord = WorkRecord.query.join(WorkSheet).filter(
            WorkSheet.user_id == user_id,
            WorkRecord.workDate == workDate
        ).first()
        if qs_workrecord:
            return jsonify({'error': 'Workdate already have data'}), 400
        new_workrecord = WorkRecord(
            worksheet_id=worksheet_id,
            workDate=workDate,
            startTime=startTime,
            endTime=endTime,
            overTime=overTime,
            lateTime=lateTime
        )
        db.session.add(new_workrecord)
        db.session.commit()
        return jsonify(WorkRecordSchema().dump(new_workrecord)), 201

    def get_workrecord_fk(user_id, id):
        workrecord = WorkRecord.query.join(WorkSheet).filter(WorkRecord.id == id, WorkSheet.user_id == user_id).first()
        if not workrecord:
            return jsonify({'message': 'WorkRecord not found'}), 404
        return jsonify(WorkRecordSchema().dump(workrecord))

    def update_workrecord_fk(user_id, id):
        workrecord = WorkRecord.query.join(WorkSheet).filter(WorkRecord.id == id, WorkSheet.user_id == user_id).first()
        if not workrecord:
            return jsonify({'message': 'WorkRecord not found'}), 404

        data = request.get_json()

        workrecord.workDate = data.get('workDate', workrecord.workDate)
        workrecord.startTime = data.get('startTime', workrecord.startTime)
        workrecord.endTime = data.get('endTime', workrecord.endTime)
        workrecord.overTime = data.get('overTime', workrecord.overTime)
        workrecord.lateTime = data.get('lateTime', workrecord.lateTime)

        db.session.commit()
        return jsonify(WorkRecordSchema().dump(workrecord)), 200

    def delete_workrecord_fk(user_id, id):
        workrecord = WorkRecord.query.join(WorkSheet).filter(WorkRecord.id == id, WorkSheet.user_id == user_id).first()
        if not workrecord:
            return jsonify({'message': 'WorkRecord not found'}), 404
        db.session.delete(workrecord)
        db.session.commit()
        return jsonify({'message': 'WorkRecord deleted successfully'}), 200



    @app.route('/profile', methods=['GET','PATCH'])
    @token_required
    def profile(user_id):
        if request.method == "GET":
            return get_profile(user_id)
        elif request.method == "PATCH":
            return update_profile(user_id)
    def get_profile(user_id):
        try:
            profile = Profile.query.filter_by(user_id=user_id).first()
            if profile:
                return jsonify(ProfileSchema().dump(profile))
            return jsonify({'message': 'Profile not found'}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    def update_profile(user_id):
        try:
            data = request.get_json()
            profile = Profile.query.filter_by(user_id=user_id).first()
            if profile:
                if 'avatar_id' in data:
                    profile.avatar_id = data['avatar_id']
                if 'wallpaper_id' in data:
                    profile.wallpaper_id = data['wallpaper_id']
                if 'full_name' in data:
                    profile.full_name = data['full_name']
                if 'full_name' in data:
                    profile.full_name = data['full_name']
                if 'zalo_name' in data:
                    profile.zalo_name = data['zalo_name']
                if 'address' in data:
                    profile.address = data['address']
                if 'huyen' in data:
                    profile.huyen = data['huyen']
                if 'tinh' in data:
                    profile.tinh = data['tinh']
                if 'long_pos' in data:
                    profile.long_pos = data['long_pos']
                if 'lat_pos' in data:
                    profile.lat_pos = data['lat_pos']
                # Thêm các trường khác cần cập nhật

                db.session.commit()
                profile = Profile.query.filter_by(user_id=user_id).first()
                return jsonify({
                    'message': 'Profile updated successfully',
                    'data':ProfileSchema().dump(profile)
                }), 200
            return jsonify({'message': 'Profile not found'}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/photos", methods=['GET'])
    @token_required
    def photos(user_id):
        if request.method == "GET":
            return get_photos(user_id)
    def get_photos(user_id):
        try:
            qs_photos = Photos.query.filter_by(user_id=user_id)
            
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            pagination = StandardPagesPagination(qs_photos, page, per_page)
            project_schema = WorkSheetSchema(many=True)
            paginated_data = pagination.to_dict(project_schema)
            return jsonify(paginated_data), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

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