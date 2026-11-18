# Giả lập database bằng dictionary / list dữ liệu người dùng
USERS = {
    1: {
        "f": "Văn",
        "l": "Nguyễn",
        "first_name": "Văn",
        "last_name": "Nguyễn",
        "email": "van.nguyen@example.com"
    },
    2: {
        "f": "Thị",
        "l": "Trần",
        "first_name": "Thị",
        "last_name": "Trần",
        "email": "thi.tran@example.com"
    },
    42: {
        "f": "Anh",
        "l": "Lê",
        "first_name": "Anh",
        "last_name": "Lê",
        "email": "anh.le@example.com"
    }
}

def get_user(uid: int):
    """
    Hàm giả lập truy vấn user theo uid từ database.
    Trả về dict user nếu tìm thấy, hoặc None nếu không có.
    """
    return USERS.get(uid)
