from flask import Flask, jsonify

app = Flask(__name__) 

library = {
    "1": {"title": "API_1", "author": "Nguyen Xuan Tuong"},
    "2": {"title": "API_2", "author": "Nguyen Xuan Tuong"}
}
def find_by_id(book_id):
    if book_id in library:
        return library.get(book_id)
    return None

@app.route("/books/<book_id>", methods=["GET"]) 
def get_book(book_id):
    book = find_by_id(book_id) 
    if not book:
        return {"Error": "Not found"}, 404
    return jsonify(book), 200 
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)