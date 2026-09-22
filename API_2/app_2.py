from flask import Flask, jsonify, request, make_response

app = Flask(__name__) 
BOOKS = [
   {"id": 0 , "title": "Practice API", "author" : "Nguyen Xuan Tuong","isbn": "78123" ,"price" : 15000}
]

# Find book by id
def find_by_id(b_id):
    for b in BOOKS:
        if(b["id"] == b_id ):
            return b
    return None
_next_id = 1 

# Get List Books 
@app.route("/books", methods=["GET"]) 
def list_book():
    return jsonify({
        "data": BOOKS, 
        "total": len(BOOKS)
    }), 200

# Create Book 
@app.route("/books", methods=["POST"]) 
def create_book(): 
    global _next_id
    b = request.get_json(silent=True) or {} 
    t = b.get("title") 
    a = b.get("author")
    if not t or not a:
        return {"error": "Need to complete title and author"}, 400
    book = {"id": _next_id, "title": t, "author": a}
    BOOKS.append(book) 
    _next_id += 1
    resp = make_response(jsonify(book), 201)
    resp.headers["Location"] = f"/books/{book['id']}"
    return resp

# GET/books/<id> ___ cache 60s
@app.get("/books/<int:bid>")
def fetch(bid):
    i = next((k for k, b in enumerate(BOOKS) if b["id"] == bid), None) 
    if i is None:
        return jsonify(error="not found"), 404
    resp = make_response(jsonify(BOOKS[i]), 200) 
    resp.headers["Cache-Control"] = "max-age=60" 
    return resp

# PUT/ Change all information
@app.put("/books/<int:bid>")
def put(bid):
    i = next((k for k, b in enumerate(BOOKS) if b["id"] == bid), None)
    if i is None:
        return jsonify(error="not found"), 404
    p = request.get_json(silent=True) or {} 
    t = p.get("title")
    a = p.get("author") 
    if not t or not a: 
        return jsonify(error = "need title + author"), 400
    BOOKS[i] = {"id": bid, "title" : t.strip(), "author" : a.strip(), "isbn" : p.get("isbn"), "price" : p.get("price")}
    return jsonify(BOOKS[i]), 200

# Patch / Change field in body
@app.patch("/books/<int:bid>") 
def patch(bid):
    i = next((k for k, b in enumerate(BOOKS) if b['id'] == bid), None)
    if i is None:
        return jsonify(error="not found"), 404
    p = request.get_json(silent=True) or {} 
    if p.get("price", 0) < 0:
        return jsonify(error="price must be positive"), 422
    for k in "title author isbn price".split():
        if k in p:
            BOOKS[i][k] = p[k] 
    return jsonify(BOOKS[i]), 200

# Delete / Delete a book
@app.delete("/books/<int:bid>") 
def delete(bid):
    i = next((k for k, b in enumerate(BOOKS) if b['id'] == bid), None) 
    if i is None:
        return jsonify(error="not found"), 404
    BOOKS.pop(i)
    return "", 204

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
    
    