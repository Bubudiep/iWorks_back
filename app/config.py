# app/config.py

import os

class Config:
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(os.path.dirname(__file__), "instance/app.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'your_secret_key_here'
