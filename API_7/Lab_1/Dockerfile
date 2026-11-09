FROM python:3.11-slim

# Tạo và chuyển vào thư mục làm việc /app trong container
WORKDIR /app

# Không tạo file .pyc và hiển thị log trực tiếp ra terminal
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copy danh sách thư viện và cài đặt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code của dự án vào container
COPY . .

# Mở cổng 5000
EXPOSE 5000

# Lệnh khởi chạy server khi bật container
CMD ["python", "wsgi.py"]
