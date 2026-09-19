from flask import Flask, jsonify, request, make_response

app = Flask(__name__) 
BOOKS = [
   {"id": 0 , "title": "Practice", "author" : "Nguyen Xuan Tuong"}
]

# Find book by id
def find_by_id(b_id):
    for b in BOOKS:
        if(b["id"] == b_id ):
            return b
    return None
_next_id = 1 
# GET book 
@app.route("/books/<int:bid>", methods=["GET"]) 
def get_book(bid):
    book = find_by_id(bid)
    if book is None:
        return {"error": "not found this book"}, 404
    return jsonify(book), 200

# Get List Books 
@app.route("/books", methods=["GET"]) 
def list_book():
    return jsonify({"data": BOOKS}, {"total": len(BOOKS)}), 200

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
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
    
    