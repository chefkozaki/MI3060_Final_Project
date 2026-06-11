from tree_algorithms import AVLTree
from datetime import datetime
from abc import ABC, abstractmethod

class IDatabaseContext(ABC):
    @abstractmethod
    def load_data(self, library_manager):
        pass

    @abstractmethod
    def save_data(self, library_manager):
        pass

    @abstractmethod
    def load_books(self, library_manager):
        pass

    @abstractmethod
    def load_readers(self, library_manager):
        pass

    @abstractmethod
    def save_borrow_record(self, record):
        pass

class FileDatabaseContext(IDatabaseContext):
    def __init__(self, books_file, readers_file, borrows_file="borrows.txt", queue_file="queue.txt"):
        self.books_file = books_file
        self.readers_file = readers_file
        self.borrows_file = borrows_file
        self.queue_file = queue_file

    def load_data(self, library_manager):
        self.load_books(library_manager)
        self.load_readers(library_manager)
        self.load_borrows(library_manager)
        self.load_queue(library_manager)

    def save_data(self, library_manager):
        self.save_books(library_manager)
        self.save_readers(library_manager)
        self.save_borrows(library_manager)
        self.save_queue(library_manager)

    def load_books(self, library_manager):
        import os
        if os.path.exists(self.books_file):
            with open(self.books_file, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) >= 4:
                        book_id = parts[0]
                        quantity = int(parts[-1])
                        author = parts[-2]
                        title = ','.join(parts[1:-2])
                        library_manager.add_book(book_id, title, author, quantity)

    def save_books(self, library_manager):
        books = library_manager.book_tree.in_order()
        with open(self.books_file, 'w', encoding='utf-8') as f:
            for b in books:
                f.write(f"{b.book_id},{b.title},{b.author},{b.total_quantity}\n")

    def load_readers(self, library_manager):
        import os
        if os.path.exists(self.readers_file):
            with open(self.readers_file, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) >= 3:
                        reader_id, name, class_name = parts[0], parts[1], parts[2]
                        library_manager.add_reader(reader_id, name, class_name)
                        if len(parts) >= 4:
                            status = int(parts[3])
                            reader = library_manager.reader_tree.search(reader_id)
                            if reader:
                                reader.status = status

    def save_readers(self, library_manager):
        readers = library_manager.reader_tree.in_order()
        with open(self.readers_file, 'w', encoding='utf-8') as f:
            for r in readers:
                f.write(f"{r.reader_id},{r.name},{r.class_name},{r.status}\n")

    def load_borrows(self, library_manager):
        import os
        if os.path.exists(self.borrows_file):
            with open(self.borrows_file, 'r', encoding='utf-8') as f:
                max_record_id = 0
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) >= 5:
                        record_id = int(parts[0])
                        reader_id = parts[1]
                        book_id = parts[2]
                        borrow_date = parts[3]
                        status = parts[4]
                        actual_return_date = parts[5] if (len(parts) >= 6 and parts[5] != "None") else None
                        
                        max_record_id = max(max_record_id, record_id)
                        
                        reader = library_manager.reader_tree.search(reader_id)
                        book = library_manager.book_tree.search(book_id)
                        
                        if reader and book:
                            record = BorrowRecord(record_id, book_id, reader_id, borrow_date)
                            record.status = status
                            record.actual_return_date = actual_return_date
                            reader.history_list.append(record)
                            if status == "Borrowed":
                                book.stock -= 1
                library_manager.record_counter = max_record_id + 1

    def save_borrows(self, library_manager):
        readers = library_manager.reader_tree.in_order()
        with open(self.borrows_file, 'w', encoding='utf-8') as f:
            for r in readers:
                current = r.history_list.head
                while current:
                    rec = current.data
                    actual_return_str = str(rec.actual_return_date) if rec.actual_return_date else "None"
                    f.write(f"{rec.record_id},{r.reader_id},{rec.book_id},{rec.borrow_date},{rec.status},{actual_return_str}\n")
                    current = current.next

    def load_queue(self, library_manager):
        import os
        if os.path.exists(self.queue_file):
            with open(self.queue_file, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) >= 2:
                        library_manager.wait_queue.enqueue(parts[0], parts[1])

    def save_queue(self, library_manager):
        with open(self.queue_file, 'w', encoding='utf-8') as f:
            current = library_manager.wait_queue.front
            while current:
                f.write(f"{current.reader_id},{current.book_id}\n")
                current = current.next

    def save_borrow_record(self, record):
        pass

class MySQLDatabaseContext(IDatabaseContext):
    def load_data(self, library_manager):
        pass
    def save_data(self, library_manager):
        pass
    def load_books(self, library_manager):
        # Implementation for MySQL loading
        pass
    def load_readers(self, library_manager):
        # Implementation for MySQL loading
        pass
    def save_borrow_record(self, record):
        # Implementation for saving to MySQL
        pass

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

