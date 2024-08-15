# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .models import db
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "http://localhost:*"}})
    app.config.from_object('app.config.Config')
    db.init_app(app)
    
    migrate = Migrate(app, db)  # Thêm cấu hình Flask-Migrate

    # Đăng ký các blueprint
    # from .routes import routes
    # app.register_blueprint(routes)
    from . import api  # Import routes
    api.init_app(app)

    return app
