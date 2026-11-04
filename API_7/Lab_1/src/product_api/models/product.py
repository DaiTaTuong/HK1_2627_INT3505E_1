from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from src.product_api.extensions import db

class Product(db.Model):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True)
    # sku: 3-32 ký tự, duy nhất để phục vụ check lỗi 409
    sku: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    # name: 1-255 ký tự
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # price_cents >= 0
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    # qty_in_stock mặc định là 0
    qty_in_stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # Cờ phục vụ soft delete (đánh dấu archived=True)
    archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)