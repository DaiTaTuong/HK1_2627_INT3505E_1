from flask.views import MethodView
from flask_smorest import Blueprint, abort, Api
from marshmallow import Schema, fields
from flask import Flask
import yaml

blp = Blueprint("product", __name__, url_prefix = "/products")
product_db = []

app = Flask(__name__)
app.config["API_TITLE"] = "My Minimal API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

api = Api(app)

class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Int(required=True)
    price = fields.Float(required=True)
@blp.route("/")
class ProductList(MethodView):
    @blp.response(200, ProductSchema)
    def get(self):
        return product_db

    @blp.arguments(ProductSchema)
    @blp.response(201, ProductSchema)
    def post(self, data):
        data['id'] = len(product_db) + 1
        product_db.append(data)
        return data

api.register_blueprint(blp)

openapi_dict = api.spec.to_dict()
with open("openapi.yaml", "w", encoding="utf-8") as f:
    yaml.dump(openapi_dict, f, allow_unicode=True, sort_keys=False)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)