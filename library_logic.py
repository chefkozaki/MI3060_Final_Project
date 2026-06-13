from tree_algorithms import AVLTree
from datetime import datetime

class BookRecord:
    def __init__(self, book_id, title, author, total_quantity, location="Chưa xác định"):
        self.book_id = str(book_id)
        self.title = str(title)
        self.author = str(author)
        self.total_quantity = int(total_quantity)
        self.stock = int(total_quantity) # available quantity
        self.location = str(location)

class ReaderRecord:
    def __init__(self, reader_id, name, class_name):
        self.reader_id = str(reader_id)
        self.name = str(name)
        self.class_name = str(class_name)
        self.status = 1 # 1: Active, 0: Locked
        self.history_list = DoublyLinkedList()

class BorrowRecord:
    def __init__(self, record_id, book_id, reader_id, borrow_date):
        self.record_id = record_id
        self.book_id = str(book_id)
        self.reader_id = str(reader_id)
        self.borrow_date = borrow_date
        self.due_date = None
        self.actual_return_date = None
        self.status = "Borrowed"

class DLLNode:
    def __init__(self, data):
        self.data = data
        self.prev = None
        self.next = None

class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def append(self, data):
        new_node = DLLNode(data)
        if not self.head:
            self.head = self.tail = new_node
        else:
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node

    def find_active_record(self, book_id):
        # Reverse traversal
        current = self.tail
        while current:
            if current.data.book_id == book_id and current.data.status == "Borrowed":
                return current.data
            current = current.prev
        return None

class QueueNode:
    def __init__(self, reader_id, book_id):
        self.reader_id = reader_id
        self.book_id = book_id
        self.next = None

class WaitQueue:
    def __init__(self):
        self.front = None
        self.rear = None

    def enqueue(self, reader_id, book_id):
        new_node = QueueNode(reader_id, book_id)
        if self.rear is None:
            self.front = self.rear = new_node
            return
        self.rear.next = new_node
        self.rear = new_node

    def dequeue(self):
        if self.front is None:
            return None
        temp = self.front
        self.front = temp.next
        if self.front is None:
            self.rear = None
        return temp

    def is_empty(self):
        return self.front is None


class LibraryManager:
    def __init__(self):
        self.book_tree = AVLTree(key_func=lambda x: x.book_id)
        self.reader_tree = AVLTree(key_func=lambda x: x.reader_id)
        self.wait_queue = WaitQueue()
        self.record_counter = 1
        self._cached_books_list = None
        self._cached_readers_list = None

    def add_book(self, book_id, title, author, quantity):
        existing_book = self.book_tree.search(book_id)
        if existing_book:
            existing_book.total_quantity += quantity
            existing_book.stock += quantity
            return True, "Đã cập nhật số lượng sách tồn tại."
        else:
            new_book = BookRecord(book_id, title, author, quantity)
            self.book_tree.insert(new_book)
            self._cached_books_list = None
            return True, "Thêm sách mới thành công."

    def update_book(self, book_id, title=None, quantity=None, location=None):
        book = self.book_tree.search(book_id)
        if not book:
            return False, "Sách không tồn tại."
        
        if title is not None:
            book.title = title
        if location is not None:
            book.location = location
        if quantity is not None:
            diff = quantity - book.total_quantity
            if book.stock + diff < 0:
                return False, "Lỗi: Số lượng mới nhỏ hơn số lượng sách đang cho mượn."
            book.total_quantity = quantity
            book.stock += diff
            
        self._cached_books_list = None
        return True, "Cập nhật sách thành công."

    def delete_book(self, book_id):
        book = self.book_tree.search(book_id)
        if not book:
            return False, "Sách không tồn tại."
        self.book_tree.delete(book_id)
        self._cached_books_list = None
        return True, "Xóa sách thành công."

    def add_reader(self, reader_id, name, class_name):
        existing = self.reader_tree.search(reader_id)
        if existing:
            return False, "Mã độc giả đã tồn tại."
        new_reader = ReaderRecord(reader_id, name, class_name)
        self.reader_tree.insert(new_reader)
        self._cached_readers_list = None
        return True, "Cấp thẻ độc giả thành công."

    def lock_reader(self, reader_id):
        reader = self.reader_tree.search(reader_id)
        if not reader:
            return False, "Độc giả không tồn tại."
        reader.status = 0
        self._cached_readers_list = None
        return True, "Đã khóa thẻ độc giả."

    def get_all_books(self):
        if self._cached_books_list is None:
            # Build borrowers map: book_id -> list of reader_ids
            readers = self.reader_tree.in_order()
            borrowers_map = {}
            for r in readers:
                current = r.history_list.head
                while current:
                    if current.data.status == "Borrowed":
                        bid = current.data.book_id
                        if bid not in borrowers_map:
                            borrowers_map[bid] = []
                        borrowers_map[bid].append(r.reader_id)
                    current = current.next

            books = self.book_tree.in_order()
            self._cached_books_list = []
            for b in books:
                borrowed_by = borrowers_map.get(b.book_id, [])
                self._cached_books_list.append({
                    "book_id": b.book_id,
                    "title": b.title,
                    "author": b.author,
                    "stock": b.stock,
                    "total_quantity": b.total_quantity,
                    "location": getattr(b, 'location', 'Chưa xác định'),
                    "borrowed_by": borrowed_by
                })
        return self._cached_books_list

    def get_all_readers(self):
        if self._cached_readers_list is None:
            readers = self.reader_tree.in_order()
            self._cached_readers_list = [{"reader_id": r.reader_id, "name": r.name, "class_name": r.class_name, "status": r.status} for r in readers]
        return self._cached_readers_list

    def handle_borrow_book(self, book_id, reader_id, date_str):
        reader = self.reader_tree.search(reader_id)
        book = self.book_tree.search(book_id)

        if not reader:
            return False, "Lỗi: Độc giả không tồn tại trên hệ thống."
        if not book:
            return False, "Lỗi: Sách không tồn tại trên hệ thống."
        
        if reader.status == 0:
            return False, "Lỗi: Thẻ độc giả đang bị khóa."
        
        if book.stock <= 0:
            self.wait_queue.enqueue(reader_id, book_id)
            return True, "Thông báo: Sách tạm hết. Đã tự động thêm vào danh sách chờ."

        book.stock -= 1
        new_record = BorrowRecord(self.record_counter, book_id, reader_id, date_str)
        self.record_counter += 1
        reader.history_list.append(new_record)
        self._cached_books_list = None # Book stock changed
        return True, "Thành công: Đã tạo phiếu mượn sách."

    def handle_return_book(self, book_id, reader_id, return_date):
        reader = self.reader_tree.search(reader_id)
        book = self.book_tree.search(book_id)

        if not reader or not book:
            return False, "Lỗi: Dữ liệu Sách hoặc Độc giả không hợp lệ."

        record = reader.history_list.find_active_record(book_id)
        if not record:
            return False, "Lỗi: Không tìm thấy giao dịch mượn phù hợp hoặc sách đã được trả."
        
        record.actual_return_date = return_date
        record.status = "Returned"

        book.stock += 1

        # Check queue
        # Since queue is simple, we might just peek and check if the next in queue wants this book.
        # But we must preserve queue order if the front is not waiting for this book.
        # However, typically a wait queue for library might be per-book. 
        # Here we have a global queue. So we should find the first person waiting for THIS book.
        prev = None
        current = self.wait_queue.front
        while current:
            if current.book_id == book_id:
                # Found a wait request for this book
                next_reader = current.reader_id
                # Remove from queue
                if prev:
                    prev.next = current.next
                    if not current.next:
                        self.wait_queue.rear = prev
                else:
                    self.wait_queue.dequeue() # it was at front
                
                # Automatically grant borrow
                self.handle_borrow_book(book_id, next_reader, return_date)
                return True, f"Đã trả sách và tự động chuyển giao cho độc giả {next_reader} đang chờ."
            prev = current
            current = current.next

        self._cached_books_list = None # Book stock changed
        return True, "Thành công: Đã trả sách và phục hồi kho."

    def get_wait_queue_list(self):
        result = []
        current = self.wait_queue.front
        while current:
            result.append({"reader_id": current.reader_id, "book_id": current.book_id})
            current = current.next
        return result

