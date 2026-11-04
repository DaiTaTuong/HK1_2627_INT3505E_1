from flask import Flask, jsonify
from src.product_api.config import Config
from src.product_api.extensions import db, ma, migrate

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Khởi tạo extensions
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)

    # Đăng ký các endpoints API
    from src.product_api.api.products import products_bp
    app.register_blueprint(products_bp)

    # Đăng ký xử lý lỗi chung để đảm bảo mọi lỗi 404/500 đều về dạng JSON
    @app.errorhandler(404)
    def handle_404(e):
        return jsonify({"error": "Not Found", "detail": "The requested URL was not found on the server."}), 404
        
    @app.errorhandler(405)
    def handle_405(e):
        return jsonify({"error": "Method Not Allowed", "detail": "The method is not allowed for the requested URL."}), 405

    @app.errorhandler(Exception)
    def handle_exception(e):
        return jsonify({"error": "Internal Server Error", "detail": str(e)}), 500

    return app