from abc import ABC, abstractmethod
import os
from library_logic import BorrowRecord

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
        pass
    def load_readers(self, library_manager):
        pass
    def save_borrow_record(self, record):
        pass
