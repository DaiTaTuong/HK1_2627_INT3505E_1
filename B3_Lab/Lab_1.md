# LAB 1: THIẾT KẾ RESOURCE CHO BLOG API

## 1. Xác định resources 

1. **Users** (`users`)

2. **Profiles** (`profiles`)

3. **Posts** (`posts`)

4. **Comments** (`comments`)

5. **Tags** (`tags`)

6. **Followers** (`followers`)

## 2. Phân Loại Collection, Item và Sub-resource

| 1. **Users** (`users`): Collection  2. **Profiles** (`profiles`): Item  3. **Posts** (`posts`):  Collection  4. **Comments** (`comments`): Sub-resource  5. **Tags** (`tags`):   6. **Followers** (`followers`): Sub-resource | Danh sách các thẻ gắn trên bài viết | 

## 3. Sơ Đồ Cây Endpoint & Version Segment

```

│
├── /users
│   ├── GET                          (Liệt kê người dùng)
│   ├── POST                         (Đăng ký tài khoản)
│   └── /{userId}
│       ├── GET                      (Xem thông tin user)
│       ├── PUT / PATCH              (Cập nhật user)
│       ├── DELETE                   (Xóa user)
│       │
│       ├── /profile
│       │   ├── GET                  (Xem hồ sơ)
│       │   └── PUT / PATCH          (Chỉnh sửa hồ sơ)
│       │
│       ├── /followers
│       │   └── GET                  (Danh sách người theo dõi user này)
│       │
│       └── /following
│           ├── GET                  (Danh sách user này đang theo dõi)
│          
│               ├── PUT              (Theo dõi / Follow tác giả)
│               └── DELETE           (Bỏ theo dõi / Unfollow)
│
├── /posts
│   ├── GET                          (Lấy danh sách bài viết - filter ?tag=..., ?author_id=...)
│   ├── POST                         (Tạo bài viết mới)
│   └── /{postId}
│       ├── GET                      (Xem chi tiết bài viết)
│       ├── PUT / PATCH              (Cập nhật bài viết)
│       ├── DELETE                   (Xóa bài viết)
│       │
│       ├── /comments
│       │   ├── GET                  (Danh sách bình luận của bài viết)
│       │   └── POST                 (Thêm bình luận vào bài viết)
│       │
│       └── /tags
│           ├── GET                  (Danh sách tags của bài viết)
│           ├── POST                 (Gắn tag vào bài viết)
│           └── /{tagId}
│               └── DELETE           (Gỡ tag khỏi bài viết)
│
├── /comments
│   └── /{commentId}
│       ├── GET                      (Xem chi tiết bình luận)
│       ├── PUT / PATCH              (Chỉnh sửa bình luận)
│       └── DELETE                   (Xóa bình luận)
│
└── /tags
    ├── GET                          (Xem danh sách tag phổ biến)
    └── POST                         (Tạo tag mới)

```

## 4. Triển Khai Flask Routes Cho Collection `/posts`

```
from flask import Flask, jsonify, request, abort

app = Flask(__name__)

# Giả lập database trong bộ nhớ
posts = [
    {
        "id": 1,
        "title": "Bắt đầu với RESTful API",
        "content": "Nội dung bài viết về các nguyên tắc REST...",
        "author_id": 101,
        "tags": ["api", "rest", "backend"]
    },
    {
        "id": 2,
        "title": "Tối ưu hóa Nesting URI",
        "content": "Không nên nest quá sâu quá 2-3 cấp...",
        "author_id": 102,
        "tags": ["architecture", "best-practices"]
    }
]
next_id = 3


# ---------------------------------------------------------
# 1. GET /api/v1/posts - Lấy danh sách bài viết (Collection)
# ---------------------------------------------------------
@app.route("/api/v1/posts", methods=["GET"])
def get_posts():
    # Hỗ trợ lọc qua query parameter: ?tag=api hoặc ?author_id=101
    tag_filter = request.args.get("tag")
    author_filter = request.args.get("author_id", type=int)

    filtered_posts = posts
    if tag_filter:
        filtered_posts = [p for p in filtered_posts if tag_filter.lower() in [t.lower() for t in p.get("tags", [])]]
    if author_filter:
        filtered_posts = [p for p in filtered_posts if p.get("author_id") == author_filter]

    return jsonify({
        "data": filtered_posts,
        "count": len(filtered_posts)
    }), 200


# ---------------------------------------------------------
# 2. POST /api/v1/posts - Tạo mới bài viết
# ---------------------------------------------------------
@app.route("/api/v1/posts", methods=["POST"])
def create_post():
    global next_id
    data = request.get_json()

    # Kiểm tra payload
    if not data or "title" not in data or "content" not in data or "author_id" not in data:
        return jsonify({
            "error": "Bad Request",
            "message": "Các trường 'title', 'content', và 'author_id' là bắt buộc."
        }), 400

    new_post = {
        "id": next_id,
        "title": data["title"],
        "content": data["content"],
        "author_id": data["author_id"],
        "tags": data.get("tags", [])
    }
    posts.append(new_post)
    next_id += 1

    # Chuẩn REST: trả về mã 201 Created kèm resource vừa tạo
    return jsonify(new_post), 201


# ---------------------------------------------------------
# 3. GET /api/v1/posts/{postId} - Lấy chi tiết một bài viết (Item)
# ---------------------------------------------------------
@app.route("/api/v1/posts/<int:post_id>", methods=["GET"])
def get_post(post_id):
    post = next((p for p in posts if p["id"] == post_id), None)
    if not post:
        return jsonify({"error": "Not Found", "message": f"Không tìm thấy bài viết ID {post_id}"}), 404
    
    return jsonify(post), 200


# ---------------------------------------------------------
# 4. PUT /api/v1/posts/{postId} - Cập nhật toàn bộ bài viết
# ---------------------------------------------------------
@app.route("/api/v1/posts/<int:post_id>", methods=["PUT"])
def update_post(post_id):
    post = next((p for p in posts if p["id"] == post_id), None)
    if not post:
        return jsonify({"error": "Not Found", "message": f"Không tìm thấy bài viết ID {post_id}"}), 404

    data = request.get_json()
    if not data or "title" not in data or "content" not in data:
        return jsonify({"error": "Bad Request", "message": "'title' và 'content' là bắt buộc khi cập nhật PUT."}), 400

    post["title"] = data["title"]
    post["content"] = data["content"]
    post["tags"] = data.get("tags", post.get("tags", []))

    return jsonify(post), 200


# ---------------------------------------------------------
# 5. DELETE /api/v1/posts/{postId} - Xóa một bài viết
# ---------------------------------------------------------
@app.route("/api/v1/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    global posts
    post = next((p for p in posts if p["id"] == post_id), None)
    if not post:
        return jsonify({"error": "Not Found", "message": f"Không tìm thấy bài viết ID {post_id}"}), 404

    posts = [p for p in posts if p["id"] != post_id]
    
    # 204 No Content: Xóa thành công, không kèm nội dung body
    return "", 204


if __name__ == "__main__":
    app.run(debug=True, port=5000)

```