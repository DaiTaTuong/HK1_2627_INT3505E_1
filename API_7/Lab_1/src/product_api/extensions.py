from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate

class Base(DeclarativeBase):
    pass

# Khởi tạo db với chuẩn SQLAlchemy 2.x
db = SQLAlchemy(model_class=Base)
ma = Marshmallow()
migrate = Migrate()