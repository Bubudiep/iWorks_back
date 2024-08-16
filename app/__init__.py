from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .models import db
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    
    # Cấu hình CORS với các domain được phép
    CORS(app, resources={r"/*": {"origins": ["https://h5.zdn.vn", "zbrowser://h5.zdn.vn", "http://localhost:*", "https://localhost:*"]}})
    
    app.config.from_object('app.config.Config')
    db.init_app(app)
    
    migrate = Migrate(app, db)  # Thêm cấu hình Flask-Migrate

    # Đăng ký các blueprint
    # Đăng ký các blueprint
    from .api import api
    app.register_blueprint(api)

    return app
