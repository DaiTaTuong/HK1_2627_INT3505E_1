from flask import Flask, jsonify, request

app = Flask(__name__)
_next = 1
BOOKS = [
    {"id": "1", "title": "Clean Code", "author": "R.Martin"} 
]

def find(b_id): 
    for b in BOOKS:
        if b["id"] == b_id:
            return b
    return None

# List - Get/books
@app.route("/books", methods= ["GET"]) 
def list_books():
    n = int(request.args.get("limit", 100)) 
    return jsonify(BOOKS[:n]), 200

# Detail - Get/books/<int:id>
@app.route("/books/<int:bid>", methods=["GET"]) 
def get_book(bid):
    book = find(bid)
    if not book:
        return {"error": "not found"}, 404
    return jsonify(book), 200

#Create - POST/books 
@app.route("/books", methods=["POST"])
def create_book(): 
    global _next
    body = request.get_json(silent=True) or {} 
    t = body.get("title") 
    a = body.get("author")
    if not t and not a:
        return {"error": "need title and author"}, 400
    elif not t:
        return {"error": "need title"}, 400
    elif not a: 
        return {"error": "need author"}, 400
    book = {"id": _next, "title" : t, "author": a} 
    _next += 1 
    BOOKS.append(book) 
    return jsonify(book), 201, {"Location":f"/books/{book['id']}"}

#Update - PUT, DELETE
@app.route("/books/<int:bid>", methods=["PUT", "DELETE"]) 
def modify_book(bid):
    book = find(bid) 
    if not book: 
        return {"error" : "not found"}, 400
    if request.method == "PUT":
        book.update(request.get_json(silent=True) or {}) 
        return jsonify(book), 200
    BOOKS.remove(book) 
    return "", 204

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)