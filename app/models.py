# app/models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=True)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # Add this line
    profile = db.relationship('Profile', backref='user', uselist=False)
    time_logs = db.relationship('TimeLog', backref='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    zalo_id = db.Column(db.String(50), unique=True, nullable=False)
    zalo_name = db.Column(db.String(50), nullable=True)
    zalo_phone = db.Column(db.String(50), nullable=True)
    full_name = db.Column(db.String(50), nullable=True)
    address = db.Column(db.String(225), nullable=True)
    huyen = db.Column(db.String(150), nullable=True)
    tinh = db.Column(db.String(150), nullable=True)
    long_pos = db.Column(db.String(50), nullable=True)
    lat_pos = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

class WorkSheet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    Company = db.Column(db.String(255), nullable=True)
    isActive = db.Column(db.Boolean, default=True, nullable=True)
    QRCode = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

class WorkSalary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    worksheet_id = db.Column(db.Integer, db.ForeignKey('work_sheet.id'), nullable=False)
    SalaryName = db.Column(db.String(255), nullable=True)
    Salary = db.Column(db.Integer, default=0, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
class WorkRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    worksheet_id = db.Column(db.Integer, db.ForeignKey('work_sheet.id'), nullable=False)
    workDate = db.Column(db.Date, default=datetime.utcnow)
    startTime = db.Column(db.DateTime, default=None, nullable=True)
    endTime = db.Column(db.DateTime, default=None, nullable=True)
    overTime = db.Column(db.Integer, default=None, nullable=True)
    lateTime = db.Column(db.Integer, default=None, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )