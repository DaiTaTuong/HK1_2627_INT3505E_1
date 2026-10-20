from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, ForeignKey, INTEGER, Table, Column
from sqlalchemy.orm import mapped_column, relationship 

db = SQLAlchemy()

book_author = Table(
    'book_author', 
    db.metadata,
    Column('book_id', ForeignKey('book.id'), primary_key=True),
    Column('author_id', ForeignKey('author.id'), primary_key=True)
)
class Book(db.Model):
    __tablename__ = 'book' 

    id = mapped_column(INTEGER, primary_key=True) 

    title = mapped_column(String(255), nullable=False) 

    authors = relationship('Author', secondary="book_author", back_populates='books')

    def to_dict(self):
        return{"id" : f"book_{self.id}", "title": self.title}

class Author(db.Model):
    __tablename__ = 'author' 

    id = mapped_column(INTEGER, primary_key=True) 
    name = mapped_column(String(150), nullable=False)

    books = relationship('Book', secondary='book_author', back_populates='authors')




