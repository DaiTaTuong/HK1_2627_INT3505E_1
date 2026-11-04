from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from marshmallow import ValidationError
from src.product_api.extensions import db
from src.product_api.models.product import Product
from src.product_api.api.schemas import ProductSchema, ProductUpdateSchema, ReserveSchema

products_bp = Blueprint('products', __name__, url_prefix='/api/v1/products')

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
product_update_schema = ProductUpdateSchema()
reserve_schema = ReserveSchema()

def error_response(status_code, error, detail):
    return jsonify({"error": error, "detail": detail}), status_code

@products_bp.route('', methods=['GET'])
def get_products():
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 20, type=int)
    
    # List mặc định loại trừ archived=True
    stmt = select(Product).where(Product.archived == False)
    pagination = db.paginate(stmt, page=page, per_page=size, error_out=False)
    
    # Chuẩn hóa cấu trúc phân trang trả về
    return jsonify({
        "items": products_schema.dump(pagination.items),
        "page": pagination.page,
        "size": pagination.per_page,
        "total": pagination.total
    }), 200

@products_bp.route('/<int:id>', methods=['GET'])
def get_product(id):
    # Get mặc định loại trừ archived=True
    product = db.session.scalar(select(Product).where(Product.id == id, Product.archived == False))
    if not product:
        return error_response(404, "Not Found", "Product not found")
    return product_schema.jsonify(product), 200

@products_bp.route('', methods=['POST'])
def create_product():
    try:
        data = request.get_json() or {}
        product = product_schema.load(data)
        db.session.add(product)
        db.session.commit()
        return product_schema.jsonify(product), 201
    except ValidationError as err:
        return error_response(422, "Validation Error", err.messages)
    except IntegrityError:
        db.session.rollback()
        # Trả về 409 nếu sku trùng
        return error_response(409, "Conflict", "SKU already exists")

@products_bp.route('/<int:id>/reserve', methods=['POST'])
def reserve_product(id):
    product = db.session.scalar(select(Product).where(Product.id == id, Product.archived == False))
    if not product:
        return error_response(404, "Not Found", "Product not found")
    
    try:
        data = request.get_json() or {}
        reserve_data = reserve_schema.load(data)
        
        # Kiểm tra không cho qty_in_stock < 0, trả về 409 nếu hết hàng
        if product.qty_in_stock < reserve_data['qty']:
            return error_response(409, "Conflict", "Not enough stock")
            
        product.qty_in_stock -= reserve_data['qty']
        db.session.commit()
        return product_schema.jsonify(product), 200
    except ValidationError as err:
        return error_response(422, "Validation Error", err.messages)

@products_bp.route('/<int:id>', methods=['PATCH'])
def update_product(id):
    product = db.session.scalar(select(Product).where(Product.id == id, Product.archived == False))
    if not product:
        return error_response(404, "Not Found", "Product not found")
    
    try:
        data = request.get_json() or {}
        # Chỉ lấy những field có trong body mới đổi
        validated_data = product_update_schema.load(data)
        
        for key, value in validated_data.items():
            setattr(product, key, value)
            
        db.session.commit()
        return product_schema.jsonify(product), 200
    except ValidationError as err:
        return error_response(422, "Validation Error", err.messages)
    except IntegrityError:
        db.session.rollback()
        return error_response(409, "Conflict", "SKU already exists")

@products_bp.route('/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = db.session.scalar(select(Product).where(Product.id == id, Product.archived == False))
    if not product:
        return error_response(404, "Not Found", "Product not found")
    
    # Soft delete (đánh dấu archived=True) thay vì xóa vật lý
    product.archived = True
    db.session.commit()
    return jsonify({"message": "Product soft-deleted successfully"}), 200