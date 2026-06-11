import sys
import io
import time
import random
import string

# Set console encoding to UTF-8 to handle Vietnamese characters on Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from tree_algorithms import AVLTree
from library_logic import BookRecord

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# --- Wrapper Classes for Array and LinkedList ---
class ArrayStructure:
    def __init__(self):
        self.data = []
        
    def insert(self, book):
        # Kiểm tra trùng lặp trước khi chèn
        if self.search(book.book_id):
            return False
        self.data.append(book)
        return True
        
    def search(self, book_id):
        for book in self.data:
            if book.book_id == book_id:
                return book
        return None

class LLNode:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedListStructure:
    def __init__(self):
        self.head = None
        
    def insert(self, book):
        # Kiểm tra trùng lặp trước khi chèn
        if self.search(book.book_id):
            return False
        new_node = LLNode(book)
        new_node.next = self.head
        self.head = new_node
        return True
        
    def search(self, book_id):
        current = self.head
        while current:
            if current.data.book_id == book_id:
                return current.data
            current = current.next
        return None

def run_tests(sizes, num_searches=5000):
    print("\n=== BẮT ĐẦU CHẠY KIỂM TRA HIỆU NĂNG TỔNG HỢP (MÔI TRƯỜNG HIGH-PRECISION) ===")
    print(f"Sử dụng: time.perf_counter() | Tìm kiếm: {num_searches:,} lượt ngẫu nhiên (90% tồn tại, 10% không tồn tại)")
    print("Lưu ý: Với các kích thước lớn (như 50,000), Array và Linked List sẽ tốn nhiều thời gian chạy (có thể từ 1-2 phút)")
    print("do phải thực hiện quét tuyến tính O(N) để kiểm tra trùng lặp cho mỗi lần chèn mới.")
    print("-" * 140)
    
    results = []
    
    for size in sizes:
        print(f"[*] Đang xử lý kích thước: {size:,} bản ghi...")
        
        # Generate random mock data
        books_data = []
        for i in range(size):
            book_id = f"B{i:05d}"
            title = generate_random_string(15)
            author = generate_random_string(10)
            stock = random.randint(1, 20)
            books_data.append(BookRecord(book_id, title, author, stock))
            
        random.shuffle(books_data)
        
        # Prepare search sample IDs (90% existing, 10% non-existing)
        num_existing = int(num_searches * 0.9)
        num_non_existing = num_searches - num_existing
        
        search_ids = []
        for _ in range(num_existing):
            search_ids.append(random.choice(books_data).book_id)
        for _ in range(num_non_existing):
            search_ids.append(f"X{random.randint(10000, 99999):05d}")
        random.shuffle(search_ids)
        
        # 1. AVL Tree
        print(f"    -> Đang chạy kiểm tra AVL Tree...")
        avl_tree = AVLTree(key_func=lambda x: x.book_id)
        start = time.perf_counter()
        for book in books_data:
            avl_tree.insert(book)
        avl_add_time = (time.perf_counter() - start) * 1000
        
        start = time.perf_counter()
        for sid in search_ids:
            avl_tree.search(sid)
        avl_search_time = (time.perf_counter() - start) * 1000
        avl_search_avg = (avl_search_time / num_searches) * 1000  # microseconds (µs)
        
        # 2. Array
        print(f"    -> Đang chạy kiểm tra Array (chờ kiểm tra trùng lặp)...")
        array_ds = ArrayStructure()
        start = time.perf_counter()
        for book in books_data:
            array_ds.insert(book)
        array_add_time = (time.perf_counter() - start) * 1000
        
        start = time.perf_counter()
        for sid in search_ids:
            array_ds.search(sid)
        array_search_time = (time.perf_counter() - start) * 1000
        array_search_avg = (array_search_time / num_searches) * 1000  # microseconds (µs)
        
        # 3. Linked List
        print(f"    -> Đang chạy kiểm tra Linked List (chờ kiểm tra trùng lặp)...")
        ll_ds = LinkedListStructure()
        start = time.perf_counter()
        for book in books_data:
            ll_ds.insert(book)
        ll_add_time = (time.perf_counter() - start) * 1000
        
        start = time.perf_counter()
        for sid in search_ids:
            ll_ds.search(sid)
        ll_search_time = (time.perf_counter() - start) * 1000
        ll_search_avg = (ll_search_time / num_searches) * 1000  # microseconds (µs)
        
        # Formatting helper
        def format_val(val):
            if val < 10:
                return f"{val:,.3f}"
            else:
                return f"{val:,.2f}"
        
        size_str = f"{size:,}"
        row = f"{size_str}\t{format_val(avl_add_time)}\t{format_val(array_add_time)}\t{format_val(ll_add_time)}\t{format_val(avl_search_time)}\t{format_val(array_search_time)}\t{format_val(ll_search_time)}"
        results.append(row)
        print(f"    [OK] Hoàn thành đo lường kích thước {size:,}!\n")

    print("\n" + "=" * 40 + " BẢNG KẾT QUẢ HIỆU NĂNG " + "=" * 40)
    print("Kích thước (Size)\tAVL Add (ms)\tArray Add (ms)\tLL Add (ms)\tAVL Search (ms)\tArray Search (ms)\tLL Search (ms)")
    for r in results:
        print(r)
    print("=" * 104)

if __name__ == "__main__":
    try:
        input_str = input("Nhập danh sách kích thước mẫu thử (cách nhau bởi dấu phẩy, ví dụ: 1000, 5000, 10000, 50000): ")
        sizes = [int(s.strip()) for s in input_str.split(",") if s.strip().isdigit()]
        if not sizes:
            print("Danh sách rỗng hoặc không hợp lệ. Sử dụng danh sách mặc định: [1000, 5000, 10000, 50000]")
            sizes = [1000, 5000, 10000, 50000]
        run_tests(sizes)
    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")
