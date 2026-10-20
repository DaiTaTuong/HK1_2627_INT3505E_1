from flask import Flask, jsonify
from lab1 import db, Book, Author

app = Flask(__name__) 

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False

db.init_app(app)

@app.get('/api/v1/books')
def get_books():
    books = Book.query.all() 
    return jsonify([book.to_dict() for book in books]) 

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)