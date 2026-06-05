import random
import os

# --- DỮ LIỆU MẪU ĐỂ TẠO TÊN ĐỘC GIẢ & TÁC GIẢ THẬT ---
LAST_NAMES = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý", "Trịnh", "Đinh"]
MIDDLE_NAMES = ["Văn", "Thị", "Hữu", "Đức", "Ngọc", "Hoàng", "Minh", "Thu", "Thanh", "Bích", "Tuấn", "Hải", "Xuân", "Hồng", "Kim", "Quốc", "Gia", "Thành"]
FIRST_NAMES = ["An", "Anh", "Bảo", "Bình", "Cường", "Châu", "Dương", "Dũng", "Đạt", "Đức", "Giang", "Hải", "Hà", "Hùng", "Hương", "Khang", "Khánh", "Linh", "Lan", "Minh", "Nam", "Nga", "Nhi", "Phúc", "Phương", "Quang", "Quyên", "Sơn", "Tài", "Thảo", "Trang", "Tuấn", "Uyên", "Vinh", "Vy", "Yến", "Thịnh", "Phong", "Phát"]

FOREIGN_AUTHORS = ["Robert C. Martin", "Martin Fowler", "Gang of Four", "Donald Knuth", "Thomas Cormen", "Andrew S. Tanenbaum", "Ian Sommerville", "Abraham Silberschatz", "Bjarne Stroustrup", "James Gosling", "Guido van Rossum"]

# --- DỮ LIỆU MẪU ĐỂ TẠO TÊN SÁCH ---
BOOK_PREFIXES = ["Giáo trình", "Nhập môn", "Cơ sở", "Kỹ thuật", "Cẩm nang", "Hướng dẫn", "Lập trình", "Phân tích", "Thiết kế", "Kiến trúc", "Nguyên lý"]
BOOK_SUBJECTS = ["C++", "Java", "Python", "C#,", "JavaScript", "Cấu trúc dữ liệu", "Giải thuật", "Cơ sở dữ liệu", "Trí tuệ nhân tạo", "Học máy", "Mạng máy tính", "Hệ điều hành", "An toàn thông tin", "Kỹ nghệ phần mềm", "Đồ họa máy tính", "Toán rời rạc", "Vi tích phân", "Vật lý đại cương", "Xác suất thống kê", "Phát triển Web", "Lập trình Mobile", "Điện toán đám mây", "IoT"]
BOOK_SUFFIXES = ["cơ bản", "nâng cao", "hiện đại", "toàn tập", "từ A đến Z", "ứng dụng", "thực hành", "cho người mới bắt đầu", "chuyên sâu", "tập 1", "tập 2"]

CLASSES = ["CNTT1", "CNTT2", "CNTT3", "KTPM1", "KTPM2", "KHMT1", "HTTT1", "KHDL1", "KHDL2", "ATTT1"]
YEARS = ["K64", "K65", "K66", "K67", "K68"]

def generate_random_name():
    return f"{random.choice(LAST_NAMES)} {random.choice(MIDDLE_NAMES)} {random.choice(FIRST_NAMES)}"

def generate_random_book_title():
    # 80% sách tiếng Việt, 20% sách chuyên ngành mộc mạc
    if random.random() < 0.8:
        pattern = random.choice([
            "{prefix} {subject} {suffix}",
            "{prefix} {subject}",
            "{subject} {suffix}"
        ])
        return pattern.format(
            prefix=random.choice(BOOK_PREFIXES),
            subject=random.choice(BOOK_SUBJECTS),
            suffix=random.choice(BOOK_SUFFIXES)
        )
    else:
        return f"{random.choice(['Mastering', 'Learning', 'Pro', 'Beginning', 'Head First'])} {random.choice(BOOK_SUBJECTS)}"

def generate_books_file(filename, count=10000):
    print(f"Generating {count} book records...")
    # Dùng set để đảm bảo title không bị trùng lặp 100% nếu cần (tuy nhiên 10000 có thể trùng)
    with open(filename, 'w', encoding='utf-8') as f:
        for i in range(1, count + 1):
            book_id = f"B{i:05d}"
            title = generate_random_book_title()
            
            if random.random() < 0.85:
                author = generate_random_name()
            else:
                author = random.choice(FOREIGN_AUTHORS)
                
            quantity = random.randint(1, 15)
            f.write(f"{book_id},{title},{author},{quantity}\n")

def generate_readers_file(filename, count=10000):
    print(f"Generating {count} reader records...")
    with open(filename, 'w', encoding='utf-8') as f:
        for i in range(1, count + 1):
            reader_id = f"R{i:05d}"
            name = generate_random_name()
            class_name = f"{random.choice(CLASSES)}-{random.choice(YEARS)}"
            f.write(f"{reader_id},{name},{class_name}\n")

if __name__ == "__main__":
    BOOKS_FILE = "books_10000.txt"
    READERS_FILE = "readers_10000.txt"
    
    generate_books_file(BOOKS_FILE, 10000)
    generate_readers_file(READERS_FILE, 10000)
    
    print("\n[SUCCESS] Generated 2 files:")
    print(f" - {BOOKS_FILE}")
    print(f" - {READERS_FILE}")
    print("Ready for upload!")
