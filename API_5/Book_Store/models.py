from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Junction table cho quan hệ N:M giữa Book và Author[cite: 10, 11]
class BookAuthor(db.Model):
    __tablename__ = 'book_authors'
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), primary_key=True)
    role = db.Column(db.String(50), default="co")

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False) # Dùng cho filter ?genre

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    price_vnd = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    
    category = db.relationship('Category', backref='books')
    authors = db.relationship('Author', secondary='book_authors', backref='books')

    def to_dict(self):
        return {
            "id": f"book_{self.id}", # Prefix ID theo chuẩn
            "title": self.title,
            "price_vnd": self.price_vnd,
            "genre": self.category.slug if self.category else None,
            "stock": self.stock
        }

class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(120))

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))