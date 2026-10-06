# Minh Chứng Hoạt Động 

Tài liệu này ghi lại quá trình kiểm thử và minh chứng kết quả chạy thực tế của Flask API xử lý lỗi chuẩn hóa theo định dạng **RFC 7807 (Problem Details for HTTP APIs)**.

## Các Ca Kiểm Thử (Test Cases)

### Test Case 1: Lấy tài nguyên hợp lệ (HTTP 200 OK)

* **Endpoint**: `GET /resources/1`

* **Mục tiêu**: Đảm bảo luồng chạy bình thường không bị ảnh hưởng bởi error handler. 

* **Kết quả khi chạy (Postman / cURL / Trình duyệt):**
* ![Ảnh chụp màn hình](API_3/1.png)

### Test Case 2: Lỗi nghiệp vụ có kiểm soát (HTTP 404 Problem Details)

* **Endpoint**: `GET /resources/2`

* **Mục tiêu**: Kiểm tra `ProblemError` được xử lý đúng chuẩn `application/problem+json`.

* **Kết quả mong đợi**:

  * **Status Code**: `404 Not Found`

  * **Content-Type**: `application/problem+json`

  * **Body**:

    ```
    {
      "detail": "Resource with id 2 does not exist.",
      "instance": "/resources/2",
      "status": 404,
      "title": "Resource Not Found",
      "type": "https://api.example.com/probs/not-found"
    }
    
    ```

* **Ảnh chụp minh chứng:**

### Test Case 3: Lỗi không lường trước - 500 Server Error

* **Endpoint**: `GET /test-crash`

* **Mục tiêu**: Kiểm tra lỗi hệ thống (chia cho 0) được bắt lại bằng `handle_unexpected_error`, không để lộ stack trace.

* **Kết quả mong đợi**:

  * **Status Code**: `500 Internal Server Error`

  * **Content-Type**: `application/problem+json`

  * **Body**:

    ```
    {
      "detail": "An unexpected error occurred. Please try again later.",
      "instance": "/test-crash",
      "status": 500,
      "title": "Internal Server Error",
      "type": "about:blank"
    }
    
    ```

* **Ảnh chụp minh chứng:**

### Test Case 4: Lỗi đường dẫn không tồn tại (Werkzeug HTTPException)

* **Endpoint**: `GET /duong-dan-khong-ton-tai`

* **Mục tiêu**: Kiểm tra `HTTPException` mặc định của Werkzeug được format lại thành Problem Details.

* **Kết quả mong đợi**:

  * **Status Code**: `404 Not Found`

  * **Content-Type**: `application/problem+json`

* **Ảnh chụp minh chứng:**
