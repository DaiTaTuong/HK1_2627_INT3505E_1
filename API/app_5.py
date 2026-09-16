from flask import Flask, jsonify
app = Flask(__name__)

ORDERS = {} 
# Delete /orders/<id>
@app.route("/orders/<id>", methods=["DELETE"]) 
def delete_order(order_id): 
    order = ORDERS.get(order_id) 

    if not order: 
        return {"error": "not found"}, 404
    if order["status"] in ("shipped", "delivered"):
        return {"error" : "can not delete"}, 409
    
    ORDERS.pop(order)
    return "", 204

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
