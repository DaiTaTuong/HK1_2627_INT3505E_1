import base64
import json
from flask import Flask, request, jsonify

app = Flask(__name__) 

ORDERS_DB = [
    {"id": 1, "customer_id": 101, "status": "paid", "total": 150.0, "created_at": "2026-01-01"},
    {"id": 2, "customer_id": 102, "status": "pending", "total": 80.0, "created_at": "2026-01-02"},
    {"id": 3, "customer_id": 101, "status": "paid", "total": 200.0, "created_at": "2026-01-03"},
    {"id": 4, "customer_id": 103, "status": "cancelled", "total": 45.0, "created_at": "2026-01-04"},
    {"id": 5, "customer_id": 101, "status": "paid", "total": 310.0, "created_at": "2026-01-05"},
    {"id": 6, "customer_id": 102, "status": "paid", "total": 120.0, "created_at": "2026-01-06"},
]

def decode_cursor(cursor_str):
    try:
        decode_bytes = base64.b64decode(cursor_str.encode("utf-8"))
        data = json.loads(decode_bytes.decode("utf-8"))
        return data.get("id")
    except Exception:
        return None

def encode_cursor(record_id):
    payload = json.dumps({"id": record_id})
    return base64.b64encode(payload.encode("utf-8")).decode("utf-8")

@app.get("/orders") 
def get_orders():
    status_filter = request.args.get("status")
    custom_id_filter = request.args.get("customer_id", type=int)

    filtered = ORDERS_DB
    if status_filter:
        filtered = [o for o in filtered if o["status"] == status_filter]
    if custom_id_filter:
        filtered = [c for c in filtered if c["customer_id"] == custom_id_filter] 

    # Xử lý cursor
    cursor = request.args.get("cursor")
    if cursor:
        last_id = decode_cursor(cursor) 
        if last_id is None:
            return jsonify({"status" : 400 , "title" : "Bad Request", "detail" : "Invalid cursor format"}) , 400
        filtered = [o for o in filtered if o["id"] > last_id]

    # Limit số trang 
    limit = request.args.get("limit", default=2, type=int)
    results = filtered[:limit]

    next_cursor = None 
    if len(filtered) > limit and results:
        next_cursor = encode_cursor(results[-1]["id"])

    field_arg = request.args.get("fields")
    if field_arg:
        selected_fields = [f.strip() for f in field_arg.split(",")]
        results = [
        {k: item[k] for k in selected_fields if k in item}
        for item in results
        ]
    return jsonify({
        "data": results,
        "pagination": {
            "limit": limit,
            "next_cursor": next_cursor
        }
    })
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
