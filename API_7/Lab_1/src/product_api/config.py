import os

class Config:
    # Mặc định dùng SQLite, có thể thay bằng chuỗi kết nối PostgreSQL thông qua .env
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False