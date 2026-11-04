from marshmallow import validate, fields
from src.product_api.extensions import ma
from src.product_api.models import Product

class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = True
        # Loại bỏ trường archived khỏi response mặc định
        exclude = ("archived",)

    # Validate chiều dài và giá trị theo yêu cầu
    sku = fields.String(required=True, validate=validate.Length(min=3, max=32))
    name = fields.String(required=True, validate=validate.Length(min=1, max=255))
    price_cents = fields.Integer(required=True, validate=validate.Range(min=0))
    qty_in_stock = fields.Integer(missing=0, validate=validate.Range(min=0))

class ProductUpdateSchema(ma.Schema):
    # Schema dành cho PATCH (cập nhật một phần), không bắt buộc phải có tất cả các field
    sku = fields.String(validate=validate.Length(min=3, max=32))
    name = fields.String(validate=validate.Length(min=1, max=255))
    price_cents = fields.Integer(validate=validate.Range(min=0))
    qty_in_stock = fields.Integer(validate=validate.Range(min=0))

class ReserveSchema(ma.Schema):
    qty = fields.Integer(required=True, validate=validate.Range(min=1))