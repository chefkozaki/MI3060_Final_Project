# Quản lý Thư viện (Library Management System)

Đây là đồ án cuối kỳ (MI3060 Final Project) - Hệ thống Quản lý Thư viện.
Dự án được xây dựng với ngôn ngữ Python, sử dụng FastAPI cho phần backend và HTML/CSS/JS cho phần frontend.

## Các tính năng chính

- **Quản lý Sách:** Thêm, sửa, xóa, tìm kiếm sách trong thư viện.
- **Quản lý Độc giả:** Thêm, tìm kiếm và xem thông tin độc giả (bao gồm lịch sử mượn), khóa tài khoản độc giả.
- **Quản lý Mượn/Trả:** Xử lý các giao dịch mượn và trả sách, quản lý hàng đợi khi sách tạm hết.
- **Tải dữ liệu hàng loạt:** Hỗ trợ nạp dữ liệu sách và độc giả từ các file đầu vào (như `books.txt`, `readers.txt`).

## Cấu trúc thư mục

- `main.py`: File chạy chính của ứng dụng FastAPI, định nghĩa các API routes.
- `library_logic.py`: Chứa các logic nghiệp vụ của thư viện (LibraryManager, Database Context).
- `tree_algorithms.py`: Triển khai các cấu trúc dữ liệu cơ sở như cây (Tree) hoặc các thuật toán tìm kiếm phục vụ ứng dụng.
- `generate_data.py`: Script dùng để sinh dữ liệu mẫu (mock data) nếu cần.
- `performance_test.py`: Script dùng để kiểm tra hiệu năng (performance test).
- `frontend/`: Thư mục chứa các tệp tin tĩnh (HTML, CSS, JS) cho giao diện người dùng.

## Cài đặt và Chạy ứng dụng

1. **Cài đặt các thư viện yêu cầu:**
   Đảm bảo bạn đã cài đặt Python. Sau đó cài đặt các thư viện cần thiết:
   ```bash
   pip install fastapi uvicorn pydantic python-multipart
   ```

2. **Chạy server:**
   Mở terminal tại thư mục gốc của dự án và khởi chạy bằng Uvicorn:
   ```bash
   python main.py
   ```
   Hoặc chạy trực tiếp với uvicorn:
   ```bash
   uvicorn main:app --reload
   ```

3. **Truy cập ứng dụng:**
   - **Giao diện Frontend:** Mở trình duyệt và truy cập [http://127.0.0.1:8000](http://127.0.0.1:8000)
   - **Tài liệu API (Swagger UI):** Để kiểm thử các API, truy cập [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
