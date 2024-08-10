# app/models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    profile = db.relationship('Profile', backref='user', uselist=False)
    time_logs = db.relationship('TimeLog', backref='user')

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    zalo_id = db.Column(db.String(50), unique=True, nullable=False)
    # Add other profile fields here

class TimeLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    check_in_time = db.Column(db.Time, nullable=False)
    check_out_time = db.Column(db.Time, nullable=False)
    overtime = db.Column(db.Interval)
    late_time = db.Column(db.Interval)
    # Add other time log fields here
