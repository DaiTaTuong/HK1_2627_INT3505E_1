import base64
import json
from flask import Blueprint, request, jsonify
from sqlalchemy import select, func, tuple_
from models import db, Book, Category

bp = Blueprint('books', __name__, url_prefix='/api/v1/books')

# Whitelist các cột cho phép sort
ALLOWED_SORT = {
    "id": Book.id,
    "price": Book.price_vnd,
    "title": Book.title,
    "stock": Book.stock
}

def encode_cursor(s):
    return base64.urlsafe_b64encode(json.dumps(s).encode()).decode().rstrip("=")

def decode_cursor(raw):
    pad = "=" * (-len(raw) % 4)
    return json.loads(base64.urlsafe_b64decode(raw + pad))

def parse_multi_sort(sort_raw):
    """Xử lý multi-key sorting: vd ?sort=-price,title[cite: 27]"""
    keys = []
    primary_sort_key = None
    primary_desc = False
    
    for idx, s in enumerate(sort_raw.split(",")):
        desc = s.startswith("-")
        name = s.lstrip("-")
        
        if name not in ALLOWED_SORT:
            return None, None, False, f"invalid_sort_column: {name}"
            
        col = ALLOWED_SORT[name]
        keys.append(col.desc() if desc else col.asc())
        
        # Lưu lại key đầu tiên làm cursor state
        if idx == 0:
            primary_sort_key = name
            primary_desc = desc
            
    # Luôn tie-break bằng ID để thứ tự được deterministic[cite: 21]
    if "id" not in sort_raw.replace("-", ""):
        keys.append(Book.id.asc())
        
    return keys, primary_sort_key, primary_desc, None

@bp.get("")
def list_books():
    strategy = request.args.get("strategy", "cursor") # Default là cursor
    lim = min(request.args.get("limit", 20, type=int), 100)
    sort_raw = request.args.get("sort", "-id")
    genre = request.args.get("genre")
    
    # 1. Parse Sort
    sort_cols, p_key, p_desc, err = parse_multi_sort(sort_raw)
    if err:
        return jsonify({"error": err}), 400

    # 2. Build Query & Filter ?genre
    q = select(Book)
    if genre:
        q = q.join(Category).filter(Category.slug == genre)
        
    q = q.order_by(*sort_cols)

    # 3. Strategy: OFFSET[cite: 20]
    if strategy == "offset":
        offset = request.args.get("offset", 0, type=int)
        total = db.session.scalar(select(func.count(Book.id)))
        rows = db.session.scalars(q.offset(offset).limit(lim)).all()
        
        return jsonify({
            "data": [b.to_dict() for b in rows],
            "pagination": {
                "strategy": "offset",
                "offset": offset,
                "limit": lim,
                "total": total,
                "has_next": offset + lim < total
            }
        })

    # 4. Strategy: CURSOR[cite: 24]
    elif strategy == "cursor":
        cursor_raw = request.args.get("cursor")
        if cursor_raw:
            try:
                c_data = decode_cursor(cursor_raw)
                # Chặn nếu user đổi sort_key giữa chừng[cite: 24, 29]
                if c_data.get("s") != p_key:
                    return jsonify({"error": "sort_changed_invalidates_cursor"}), 400
                
                v, i = c_data["v"], c_data["i"]
                op = "<" if p_desc else ">"
                condition = tuple_(ALLOWED_SORT[p_key], Book.id).op(op)((v, i))
                q = q.filter(condition)
            except Exception:
                return jsonify({"error": "invalid_cursor_format"}), 400

        # Fetch limit + 1 để check has_more[cite: 21]
        rows = db.session.scalars(q.limit(lim + 1)).all()
        has_more = len(rows) > lim
        items = rows[:lim]
        
        next_cursor = None
        if items and has_more:
            last = items[-1]
            p_col_val = getattr(last, ALLOWED_SORT[p_key].name)
            next_cursor = encode_cursor({"s": p_key, "v": p_col_val, "i": last.id})

        return jsonify({
            "data": [b.to_dict() for b in items],
            "pagination": {
                "strategy": "cursor",
                "next_cursor": next_cursor,
                "has_more": has_more
            }
        })
        
    return jsonify({"error": "invalid_strategy"}), 400