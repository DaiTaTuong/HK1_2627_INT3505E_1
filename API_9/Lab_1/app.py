from flask import Flask
from bluesprint_v1 import bp as v1_bp
from bluesprint_v2 import bp as v2_bp

app = Flask(__name__) 
app.register_blueprint(v1_bp, url_prefix = "/api/v1")
app.register_blueprint(v2_bp, url_prefix = "/api/v2")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)