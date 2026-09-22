import math
import sqlite3
from flask import Flask, g, jsonify, make_response, request

app = Flask(__name__)
DB_NAME = "books.db"
DEFAULT_SIZE = 20
MAX_SIZE = 100


# -----------------------------------------------------------------------------
# 1. HÀM QUẢN LÝ KẾT NỐI DATABASE VÀ ROW_FACTORY
# -----------------------------------------------------------------------------
def get_db():
    # Sử dụng 'g' của Flask để tái sử dụng connection trong suốt vòng đời của một request
    if "db" not in g:
        g.db = sqlite3.connect(DB_NAME)
        # sqlite3.Row cho phép truy cập cột qua tên dictionary (ví dụ: row["title"])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    # Tự động đóng connection khi request kết thúc
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    # Tạo bảng mẫu nếu chưa có
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                price REAL NOT NULL
            )
        """
        )
        conn.commit()


# -----------------------------------------------------------------------------
# 2. ENDPOINT GET /books (PHÂN TRANG + LỌC TRÊN SQLITE)
# -----------------------------------------------------------------------------
@app.get("/books")
def list_books():
    # Lấy và validate query params
    try:
        page = int(request.args.get("page", 1))
        size = int(request.args.get("size", DEFAULT_SIZE))
    except ValueError:
        return jsonify(error="page and size must be int"), 400

    page = max(page, 1)
    size = max(min(size, MAX_SIZE), 1)
    offset = (page - 1) * size

    # Xây dựng câu truy vấn SQL động theo bộ lọc
    conditions = []
    params = []

    author = request.args.get("author")
    if author:
        conditions.append("LOWER(author) = LOWER(?)")
        params.append(author)

    raw_q = request.args.get("q")
    if raw_q:
        conditions.append("LOWER(title) LIKE LOWER(?)")
        params.append(f"%{raw_q}%")

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    db = get_db()

    # Bước A: Đếm tổng số bản ghi khớp điều kiện
    count_sql = f"SELECT COUNT(*) FROM books {where_clause}"
    total = db.execute(count_sql, params).fetchone()[0]

    # Bước B: Lấy dữ liệu theo LIMIT và OFFSET (Phân trang ở DB)
    data_sql = f"SELECT * FROM books {where_clause} LIMIT ? OFFSET ?"
    query_params = params + [size, offset]
    cursor = db.execute(data_sql, query_params)

    # Chuyển kết quả sqlite3.Row thành danh sách dictionary
    items = [dict(row) for row in cursor.fetchall()]

    total_pages = max(1, math.ceil(total / size))

    # Bước C: Tạo các liên kết HATEOAS
    def u(p):
        url = f"/books?page={p}&size={size}"
        if author:
            url += f"&author={author}"
        if raw_q:
            url += f"&q={raw_q}"
        return url

    links = {
        "self": {"href": u(page)},
        "first": {"href": u(1)},
        "last": {"href": u(total_pages)},
    }
    if page > 1:
        links["prev"] = {"href": u(page - 1)}
    if page < total_pages:
        links["next"] = {"href": u(page + 1)}

    body = {
        "data": items,
        "pagination": {
            "page": page,
            "size": size,
            "total": total,
            "total_pages": total_pages,
        },
        "_links": links,
    }

    resp = make_response(jsonify(body), 200)
    resp.headers["Cache-Control"] = "public, max-age=30"
    return resp


# -----------------------------------------------------------------------------
# 3. CÁC ENDPOINT CRUD CƠ BẢN VỚI SQLITE
# -----------------------------------------------------------------------------
@app.post("/books")
def create_book():
    data = request.get_json() or {}
    if not all(k in data for k in ("title", "author", "price")):
        return jsonify(error="Missing required fields: title, author, price"), 400

    db = get_db()
    cursor = db.execute(
        "INSERT INTO books (title, author, price) VALUES (?, ?, ?)",
        (data["title"], data["author"], data["price"]),
    )
    db.commit()

    new_id = cursor.lastrowid
    new_book = {
        "id": new_id,
        "title": data["title"],
        "author": data["author"],
        "price": data["price"],
    }

    # REST chuẩn: Trả về 201 Created kèm header Location
    resp = make_response(jsonify(new_book), 201)
    resp.headers["Location"] = f"/books/{new_id}"
    return resp


@app.get("/books/<int:bid>")
def get_book(bid):
    db = get_db()
    row = db.execute("SELECT * FROM books WHERE id = ?", (bid,)).fetchone()
    if not row:
        return jsonify(error="Not Found"), 404
    return jsonify(dict(row)), 200


@app.delete("/books/<int:bid>")
def delete_book(bid):
    db = get_db()
    cursor = db.execute("DELETE FROM books WHERE id = ?", (bid,))
    db.commit()
    if cursor.rowcount == 0:
        return jsonify(error="Not Found"), 404
    return "", 204  # 204 No Content


if __name__ == "__main__":
    init_db()  # Khởi tạo bảng DB trước khi chạy app
    app.run(debug=True, port=5000)