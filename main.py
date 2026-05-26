import customtkinter as ctk
import tkinter.messagebox as msgbox
import tkinter.filedialog as filedialog
from datetime import datetime

# --- DATA STRUCTURES (Python equivalent of C++ core) ---
class BookRecord:
    def __init__(self, book_id, title, author, stock, location="Kho chung"):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.stock = stock
        self.location = location

class ReaderRecord:
    def __init__(self, reader_id, name, class_name, is_locked=False):
        self.reader_id = reader_id
        self.name = name
        self.class_name = class_name
        self.is_locked = is_locked

class AVLNode:
    def __init__(self, data):
        self.data_ptr = data
        self.left = None
        self.right = None
        self.height = 1

class AVLTree:
    def __init__(self, key_getter):
        self.root = None
        self.get_key = key_getter

    def get_height(self, node):
        if not node: return 0
        return node.height

    def get_balance(self, node):
        if not node: return 0
        return self.get_height(node.left) - self.get_height(node.right)

    def right_rotate(self, y):
        x = y.left
        T2 = x.right
        x.right = y
        y.left = T2
        y.height = max(self.get_height(y.left), self.get_height(y.right)) + 1
        x.height = max(self.get_height(x.left), self.get_height(x.right)) + 1
        return x

    def left_rotate(self, x):
        y = x.right
        T2 = y.left
        y.left = x
        x.right = T2
        x.height = max(self.get_height(x.left), self.get_height(x.right)) + 1
        y.height = max(self.get_height(y.left), self.get_height(y.right)) + 1
        return y

    def insert(self, root, data):
        if not root: return AVLNode(data)
        
        key = self.get_key(data)
        root_key = self.get_key(root.data_ptr)

        if key < root_key:
            root.left = self.insert(root.left, data)
        elif key > root_key:
            root.right = self.insert(root.right, data)
        else:
            return root

        root.height = 1 + max(self.get_height(root.left), self.get_height(root.right))
        balance = self.get_balance(root)

        if balance > 1 and key < self.get_key(root.left.data_ptr):
            return self.right_rotate(root)
        if balance < -1 and key > self.get_key(root.right.data_ptr):
            return self.left_rotate(root)
        if balance > 1 and key > self.get_key(root.left.data_ptr):
            root.left = self.left_rotate(root.left)
            return self.right_rotate(root)
        if balance < -1 and key < self.get_key(root.right.data_ptr):
            root.right = self.right_rotate(root.right)
            return self.left_rotate(root)

        return root

    def insert_node(self, data):
        self.root = self.insert(self.root, data)

    def search(self, root, key):
        if not root or self.get_key(root.data_ptr) == key:
            return root
        if self.get_key(root.data_ptr) < key:
            return self.search(root.right, key)
        return self.search(root.left, key)

    def search_node(self, key):
        res = self.search(self.root, key)
        return res.data_ptr if res else None

    def get_min_value_node(self, node):
        if node is None or node.left is None:
            return node
        return self.get_min_value_node(node.left)

    def delete(self, root, key):
        if not root:
            return root

        root_key = self.get_key(root.data_ptr)
        if key < root_key:
            root.left = self.delete(root.left, key)
        elif key > root_key:
            root.right = self.delete(root.right, key)
        else:
            if root.left is None:
                temp = root.right
                root = None
                return temp
            elif root.right is None:
                temp = root.left
                root = None
                return temp

            temp = self.get_min_value_node(root.right)
            root.data_ptr = temp.data_ptr
            root.right = self.delete(root.right, self.get_key(temp.data_ptr))

        if root is None:
            return root

        root.height = 1 + max(self.get_height(root.left), self.get_height(root.right))
        balance = self.get_balance(root)

        if balance > 1 and self.get_balance(root.left) >= 0:
            return self.right_rotate(root)
        if balance < -1 and self.get_balance(root.right) <= 0:
            return self.left_rotate(root)
        if balance > 1 and self.get_balance(root.left) < 0:
            root.left = self.left_rotate(root.left)
            return self.right_rotate(root)
        if balance < -1 and self.get_balance(root.right) > 0:
            root.right = self.right_rotate(root.right)
            return self.left_rotate(root)

        return root

    def delete_node(self, key):
        self.root = self.delete(self.root, key)

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
        temp = QueueNode(reader_id, book_id)
        if not self.rear:
            self.front = self.rear = temp
            return
        self.rear.next = temp
        self.rear = temp

    def dequeue(self):
        if not self.front: return None
        temp = self.front
        self.front = self.front.next
        if not self.front: self.rear = None
        return temp

    def is_empty(self):
        return self.front is None

class BorrowRecord:
    def __init__(self, rec_id, book_id, reader_id, b_date, d_date, r_date, status):
        self.record_id = rec_id
        self.book_id = book_id
        self.reader_id = reader_id
        self.borrow_date = b_date
        self.due_date = d_date
        self.actual_return_date = r_date
        self.status = status

class DLLNode:
    def __init__(self, data):
        self.data = data
        self.prev = None
        self.next = None

class LibraryManager:
    def __init__(self):
        self.book_tree = AVLTree(lambda x: x.book_id)
        self.reader_tree = AVLTree(lambda x: x.reader_id)
        self.wait_queue = WaitQueue()
        self.history_head = None
        self.history_tail = None
    
    def append_dll(self, record):
        node = DLLNode(record)
        if not self.history_tail:
            self.history_head = self.history_tail = node
        else:
            self.history_tail.next = node
            node.prev = self.history_tail
            self.history_tail = node

    def find_active(self, reader_id, book_id):
        curr = self.history_tail
        while curr:
            if curr.data.reader_id == reader_id and curr.data.book_id == book_id and curr.data.status == "Borrowed":
                return curr
            curr = curr.prev
        return None

    def borrow_book(self, r_id, b_id, date):
        r = self.reader_tree.search_node(r_id)
        b = self.book_tree.search_node(b_id)
        if not r: return "Error: Độc giả không tồn tại."
        if not b: return "Error: Sách không tồn tại."
        if r.is_locked: return "Error: Thẻ độc giả đang bị khóa."
        
        if b.stock <= 0:
            self.wait_queue.enqueue(r_id, b_id)
            return "Sách tạm hết. Đã thêm độc giả vào danh sách chờ."
            
        b.stock -= 1
        rec = BorrowRecord(f"{r_id}_{b_id}_{date}", b_id, r_id, date, "N/A", "", "Borrowed")
        self.append_dll(rec)
        return "Thành công: Đã cho mượn sách."

    def return_book(self, r_id, b_id, date):
        r = self.reader_tree.search_node(r_id)
        b = self.book_tree.search_node(b_id)
        if not r or not b: return "Error: Sai ID sách hoặc độc giả."
        
        rec_node = self.find_active(r_id, b_id)
        if not rec_node: return "Error: Không tìm thấy phiếu mượn tương ứng."
        
        rec_node.data.actual_return_date = date
        rec_node.data.status = "Returned"
        b.stock += 1
        
        if not self.wait_queue.is_empty() and self.wait_queue.front.book_id == b_id:
            q_node = self.wait_queue.dequeue()
            msg = self.borrow_book(q_node.reader_id, q_node.book_id, date)
            return f"Đã trả sách. {msg}"
        
        return "Thành công: Đã nhận lại sách."

    def add_or_update_book(self, book_id, title, author, stock, location):
        existing_book = self.book_tree.search_node(book_id)
        if existing_book:
            existing_book.stock += stock
            existing_book.title = title
            existing_book.author = author
            existing_book.location = location
            return "Thành công: Đã cập nhật sách tồn tại."
        else:
            self.book_tree.insert_node(BookRecord(book_id, title, author, stock, location))
            return "Thành công: Đã thêm sách mới."

    def delete_book(self, book_id):
        existing_book = self.book_tree.search_node(book_id)
        if not existing_book:
            return "Lỗi: Không tìm thấy sách."
        self.book_tree.delete_node(book_id)
        return "Thành công: Đã xóa sách khỏi hệ thống."

    def search_book_info(self, book_id):
        return self.book_tree.search_node(book_id)

    def add_reader(self, reader_id, name, class_name):
        existing_reader = self.reader_tree.search_node(reader_id)
        if existing_reader:
            return "Lỗi: Mã độc giả đã tồn tại."
        self.reader_tree.insert_node(ReaderRecord(reader_id, name, class_name))
        return "Thành công: Đã cấp thẻ độc giả mới."

    def delete_reader(self, reader_id):
        existing_reader = self.reader_tree.search_node(reader_id)
        if not existing_reader:
            return "Lỗi: Không tìm thấy thẻ độc giả."
        self.reader_tree.delete_node(reader_id)
        return "Thành công: Đã xóa thẻ độc giả."

    def lock_reader(self, reader_id):
        existing_reader = self.reader_tree.search_node(reader_id)
        if not existing_reader:
            return "Lỗi: Không tìm thấy thẻ độc giả."
        existing_reader.is_locked = not existing_reader.is_locked
        status = "Khóa" if existing_reader.is_locked else "Mở khóa"
        return f"Thành công: Đã {status} thẻ độc giả."

    def search_reader_info(self, reader_id):
        return self.reader_tree.search_node(reader_id)

    def get_borrowed_books_by_reader(self, reader_id):
        borrowed = []
        curr = self.history_tail
        while curr:
            if curr.data.reader_id == reader_id and curr.data.status == "Borrowed":
                borrowed.append(curr.data.book_id)
            curr = curr.prev
        return borrowed

    def get_readers_borrowing_book(self, book_id):
        borrowers = []
        curr = self.history_tail
        while curr:
            if curr.data.book_id == book_id and curr.data.status == "Borrowed":
                borrowers.append(curr.data.reader_id)
            curr = curr.prev
        return borrowers

# --- GUI APPLICATION ---
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Hệ thống Quản lý Thư viện - Windows 11 Fluent")
        self.geometry("900x550")
        self.manager = LibraryManager()
        self.db_mode = "Text" # Text or MySQL
        
        # Grid layout (1x2)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(8, weight=1)
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="Library System", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.btn_borrow = ctk.CTkButton(self.sidebar, text="Mượn Sách", command=lambda: self.show_frame("borrow"))
        self.btn_borrow.grid(row=1, column=0, padx=20, pady=10)
        
        self.btn_return = ctk.CTkButton(self.sidebar, text="Trả Sách", command=lambda: self.show_frame("return"))
        self.btn_return.grid(row=2, column=0, padx=20, pady=10)
        
        self.btn_add_book_data = ctk.CTkButton(self.sidebar, text="Nạp Dữ liệu Sách", command=self.load_book_data)
        self.btn_add_book_data.grid(row=3, column=0, padx=20, pady=10)
        
        self.btn_add_reader_data = ctk.CTkButton(self.sidebar, text="Nạp Dữ liệu Độc Giả", command=self.load_reader_data)
        self.btn_add_reader_data.grid(row=4, column=0, padx=20, pady=10)
        
        self.btn_manage_book = ctk.CTkButton(self.sidebar, text="Quản lý Sách", command=lambda: self.show_frame("manage_book"))
        self.btn_manage_book.grid(row=5, column=0, padx=20, pady=10)

        self.btn_manage_reader = ctk.CTkButton(self.sidebar, text="Quản lý Độc Giả", command=lambda: self.show_frame("manage_reader"))
        self.btn_manage_reader.grid(row=6, column=0, padx=20, pady=10)
        
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar, text="Giao diện (Sáng/Tối):", anchor="w")
        self.appearance_mode_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar, values=["Light", "Dark", "System"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 10))
        self.appearance_mode_optionemenu.set("Dark")
        
        self.db_mode_label = ctk.CTkLabel(self.sidebar, text="Cơ sở dữ liệu:", anchor="w")
        self.db_mode_label.grid(row=9, column=0, padx=20, pady=(10, 0))
        self.db_mode_optionmenu = ctk.CTkOptionMenu(self.sidebar, values=["Text File", "MySQL"], command=self.change_db_mode)
        self.db_mode_optionmenu.grid(row=10, column=0, padx=20, pady=(10, 20))
        
        # --- Main Frame ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        self.frames = {}
        
        # Borrow Frame
        self.frame_borrow = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frames["borrow"] = self.frame_borrow
        ctk.CTkLabel(self.frame_borrow, text="MƯỢN SÁCH", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=40)
        
        self.entry_r_id_b = ctk.CTkEntry(self.frame_borrow, placeholder_text="Nhập Mã Độc Giả", width=300, height=40)
        self.entry_r_id_b.pack(pady=10)
        self.entry_b_id_b = ctk.CTkEntry(self.frame_borrow, placeholder_text="Nhập Mã Sách", width=300, height=40)
        self.entry_b_id_b.pack(pady=10)
        self.btn_submit_borrow = ctk.CTkButton(self.frame_borrow, text="Thực Hiện", width=200, height=40, command=self.process_borrow)
        self.btn_submit_borrow.pack(pady=30)
        self.lbl_msg_b = ctk.CTkLabel(self.frame_borrow, text="", text_color="green", font=ctk.CTkFont(size=14))
        self.lbl_msg_b.pack(pady=10)
        
        # Return Frame
        self.frame_return = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frames["return"] = self.frame_return
        ctk.CTkLabel(self.frame_return, text="TRẢ SÁCH", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=40)
        
        self.entry_r_id_r = ctk.CTkEntry(self.frame_return, placeholder_text="Nhập Mã Độc Giả", width=300, height=40)
        self.entry_r_id_r.pack(pady=10)
        self.entry_b_id_r = ctk.CTkEntry(self.frame_return, placeholder_text="Nhập Mã Sách", width=300, height=40)
        self.entry_b_id_r.pack(pady=10)
        self.btn_submit_return = ctk.CTkButton(self.frame_return, text="Thực Hiện", width=200, height=40, command=self.process_return)
        self.btn_submit_return.pack(pady=30)
        self.lbl_msg_r = ctk.CTkLabel(self.frame_return, text="", text_color="green", font=ctk.CTkFont(size=14))
        self.lbl_msg_r.pack(pady=10)
        
        self.setup_book_management()
        self.setup_reader_management()
        self.show_frame("borrow")
        
        
    def setup_book_management(self):
        self.frame_manage_book = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frames["manage_book"] = self.frame_manage_book
        ctk.CTkLabel(self.frame_manage_book, text="QUẢN LÝ SÁCH", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)

        form_frame = ctk.CTkFrame(self.frame_manage_book, fg_color="transparent")
        form_frame.pack(pady=10)
        self.entry_b_id = ctk.CTkEntry(form_frame, placeholder_text="Mã Sách (ID)", width=200)
        self.entry_b_id.grid(row=0, column=0, padx=10, pady=5)
        self.entry_b_title = ctk.CTkEntry(form_frame, placeholder_text="Tên Sách", width=200)
        self.entry_b_title.grid(row=0, column=1, padx=10, pady=5)
        self.entry_b_author = ctk.CTkEntry(form_frame, placeholder_text="Tác giả", width=200)
        self.entry_b_author.grid(row=1, column=0, padx=10, pady=5)
        self.entry_b_stock = ctk.CTkEntry(form_frame, placeholder_text="Số lượng", width=200)
        self.entry_b_stock.grid(row=1, column=1, padx=10, pady=5)
        self.entry_b_location = ctk.CTkEntry(form_frame, placeholder_text="Vị trí", width=420)
        self.entry_b_location.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

        btn_frame = ctk.CTkFrame(self.frame_manage_book, fg_color="transparent")
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Tìm kiếm", width=100, command=self.search_book_action).grid(row=0, column=0, padx=5)
        ctk.CTkButton(btn_frame, text="Thêm / Cập nhật", width=100, command=self.add_update_book_action).grid(row=0, column=1, padx=5)
        ctk.CTkButton(btn_frame, text="Xóa Sách", width=100, command=self.delete_book_action, fg_color="red").grid(row=0, column=2, padx=5)

        self.lbl_book_result = ctk.CTkLabel(self.frame_manage_book, text="", text_color="green", font=ctk.CTkFont(size=14))
        self.lbl_book_result.pack(pady=10)
        
        self.txt_book_info = ctk.CTkTextbox(self.frame_manage_book, width=500, height=150)
        self.txt_book_info.pack(pady=10)

    def search_book_action(self):
        b_id = self.entry_b_id.get()
        if not b_id:
            self.lbl_book_result.configure(text="Vui lòng nhập Mã Sách!", text_color="red")
            return
        book = self.manager.search_book_info(b_id)
        self.txt_book_info.delete("1.0", "end")
        if book:
            borrowers = self.manager.get_readers_borrowing_book(book.book_id)
            borrow_status = f"\nĐang được mượn bởi: {', '.join(borrowers) if borrowers else 'Không có'}"
            
            self.lbl_book_result.configure(text="Tìm thấy sách!", text_color="green")
            info = f"Mã sách: {book.book_id}\nTên sách: {book.title}\nTác giả: {book.author}\nSố lượng tồn: {book.stock}\nVị trí: {book.location}{borrow_status}"
            self.txt_book_info.insert("1.0", info)
            self.entry_b_title.delete(0, "end")
            self.entry_b_title.insert(0, book.title)
            self.entry_b_author.delete(0, "end")
            self.entry_b_author.insert(0, book.author)
            self.entry_b_stock.delete(0, "end")
            self.entry_b_stock.insert(0, str(book.stock))
            self.entry_b_location.delete(0, "end")
            self.entry_b_location.insert(0, book.location)
        else:
            self.lbl_book_result.configure(text="Không tìm thấy sách!", text_color="red")

    def add_update_book_action(self):
        b_id = self.entry_b_id.get()
        if not b_id:
            self.lbl_book_result.configure(text="Vui lòng nhập Mã Sách!", text_color="red")
            return
        title = self.entry_b_title.get() or "Unknown"
        author = self.entry_b_author.get() or "Unknown"
        try:
            stock = int(self.entry_b_stock.get() or 0)
        except ValueError:
            stock = 0
        location = self.entry_b_location.get() or "Kho chung"
        
        res = self.manager.add_or_update_book(b_id, title, author, stock, location)
        col = "green" if "Thành công" in res else "red"
        self.lbl_book_result.configure(text=res, text_color=col)

    def delete_book_action(self):
        b_id = self.entry_b_id.get()
        if not b_id:
            self.lbl_book_result.configure(text="Vui lòng nhập Mã Sách!", text_color="red")
            return
        res = self.manager.delete_book(b_id)
        col = "green" if "Thành công" in res else "red"
        self.lbl_book_result.configure(text=res, text_color=col)
        if "Thành công" in res:
            self.txt_book_info.delete("1.0", "end")

    def setup_reader_management(self):
        self.frame_manage_reader = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frames["manage_reader"] = self.frame_manage_reader
        ctk.CTkLabel(self.frame_manage_reader, text="QUẢN LÝ ĐỘC GIẢ", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)

        form_frame = ctk.CTkFrame(self.frame_manage_reader, fg_color="transparent")
        form_frame.pack(pady=10)
        self.entry_r_id = ctk.CTkEntry(form_frame, placeholder_text="Mã Độc giả", width=200)
        self.entry_r_id.grid(row=0, column=0, padx=10, pady=5)
        self.entry_r_name = ctk.CTkEntry(form_frame, placeholder_text="Họ và Tên", width=200)
        self.entry_r_name.grid(row=0, column=1, padx=10, pady=5)
        self.entry_r_class = ctk.CTkEntry(form_frame, placeholder_text="Lớp", width=420)
        self.entry_r_class.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

        btn_frame = ctk.CTkFrame(self.frame_manage_reader, fg_color="transparent")
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Tìm kiếm", width=100, command=self.search_reader_action).grid(row=0, column=0, padx=5)
        ctk.CTkButton(btn_frame, text="Cấp thẻ mới", width=100, command=self.add_reader_action).grid(row=0, column=1, padx=5)
        ctk.CTkButton(btn_frame, text="Khóa/Mở thẻ", width=100, command=self.lock_reader_action, fg_color="orange").grid(row=0, column=2, padx=5)
        ctk.CTkButton(btn_frame, text="Xóa thẻ", width=100, command=self.delete_reader_action, fg_color="red").grid(row=0, column=3, padx=5)

        self.lbl_reader_result = ctk.CTkLabel(self.frame_manage_reader, text="", text_color="green", font=ctk.CTkFont(size=14))
        self.lbl_reader_result.pack(pady=10)
        
        self.txt_reader_info = ctk.CTkTextbox(self.frame_manage_reader, width=500, height=150)
        self.txt_reader_info.pack(pady=10)

    def search_reader_action(self):
        r_id = self.entry_r_id.get()
        if not r_id:
            self.lbl_reader_result.configure(text="Vui lòng nhập Mã Độc giả!", text_color="red")
            return
        reader = self.manager.search_reader_info(r_id)
        self.txt_reader_info.delete("1.0", "end")
        if reader:
            borrowed_books = self.manager.get_borrowed_books_by_reader(reader.reader_id)
            borrow_status = f"\nSách đang mượn: {', '.join(borrowed_books) if borrowed_books else 'Không có'}"
            
            self.lbl_reader_result.configure(text="Tìm thấy độc giả!", text_color="green")
            status = "Đang khóa" if reader.is_locked else "Bình thường"
            info = f"Mã độc giả: {reader.reader_id}\nHọ tên: {reader.name}\nLớp: {reader.class_name}\nTrạng thái thẻ: {status}{borrow_status}"
            self.txt_reader_info.insert("1.0", info)
            self.entry_r_name.delete(0, "end")
            self.entry_r_name.insert(0, reader.name)
            self.entry_r_class.delete(0, "end")
            self.entry_r_class.insert(0, reader.class_name)
        else:
            self.lbl_reader_result.configure(text="Không tìm thấy độc giả!", text_color="red")

    def add_reader_action(self):
        r_id = self.entry_r_id.get()
        if not r_id:
            self.lbl_reader_result.configure(text="Vui lòng nhập Mã Độc giả!", text_color="red")
            return
        name = self.entry_r_name.get() or "Unknown"
        class_name = self.entry_r_class.get() or "Unknown"
        
        res = self.manager.add_reader(r_id, name, class_name)
        col = "green" if "Thành công" in res else "red"
        self.lbl_reader_result.configure(text=res, text_color=col)

    def lock_reader_action(self):
        r_id = self.entry_r_id.get()
        if not r_id:
            self.lbl_reader_result.configure(text="Vui lòng nhập Mã Độc giả!", text_color="red")
            return
        res = self.manager.lock_reader(r_id)
        col = "green" if "Thành công" in res else "red"
        self.lbl_reader_result.configure(text=res, text_color=col)
        self.search_reader_action()

    def delete_reader_action(self):
        r_id = self.entry_r_id.get()
        if not r_id:
            self.lbl_reader_result.configure(text="Vui lòng nhập Mã Độc giả!", text_color="red")
            return
        res = self.manager.delete_reader(r_id)
        col = "green" if "Thành công" in res else "red"
        self.lbl_reader_result.configure(text=res, text_color=col)
        if "Thành công" in res:
            self.txt_reader_info.delete("1.0", "end")

    def load_book_data(self):
        books_file = filedialog.askopenfilename(
            title="Chọn file dữ liệu sách",
            filetypes=(("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*"))
        )
        if not books_file:
            return

        try:
            book_count = 0
            with open(books_file, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) >= 4:
                        book_id, title, author, stock = parts[0], parts[1], parts[2], int(parts[3])
                        self.manager.book_tree.insert_node(BookRecord(book_id, title, author, stock))
                        book_count += 1
            msgbox.showinfo("Thành công", f"Đã nạp {book_count} sách vào cây AVL!")
        except Exception as e:
            msgbox.showerror("Lỗi", f"Có lỗi xảy ra khi đọc file sách:\n{e}")

    def load_reader_data(self):
        readers_file = filedialog.askopenfilename(
            title="Chọn file dữ liệu độc giả",
            filetypes=(("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*"))
        )
        if not readers_file:
            return

        try:
            reader_count = 0
            with open(readers_file, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) >= 4:
                        reader_id, name, class_name, is_locked = parts[0], parts[1], parts[2], parts[3].lower() == 'true'
                        self.manager.reader_tree.insert_node(ReaderRecord(reader_id, name, class_name, is_locked))
                        reader_count += 1
            msgbox.showinfo("Thành công", f"Đã nạp {reader_count} độc giả vào cây AVL!")
        except Exception as e:
            msgbox.showerror("Lỗi", f"Có lỗi xảy ra khi đọc file độc giả:\n{e}")

    def show_frame(self, name):
        for f in self.frames.values():
            f.pack_forget()
        self.frames[name].pack(fill="both", expand=True)
        
    def process_borrow(self):
        r_id = self.entry_r_id_b.get()
        b_id = self.entry_b_id_b.get()
        date = datetime.now().strftime("%Y-%m-%d")
        if not r_id or not b_id:
            self.lbl_msg_b.configure(text="Vui lòng nhập đủ thông tin!", text_color="red")
            return
        res = self.manager.borrow_book(r_id, b_id, date)
        col = "green" if "Thành công" in res else "orange" if "Sách tạm hết" in res else "red"
        self.lbl_msg_b.configure(text=res, text_color=col)
        
    def process_return(self):
        r_id = self.entry_r_id_r.get()
        b_id = self.entry_b_id_r.get()
        date = datetime.now().strftime("%Y-%m-%d")
        if not r_id or not b_id:
            self.lbl_msg_r.configure(text="Vui lòng nhập đủ thông tin!", text_color="red")
            return
        res = self.manager.return_book(r_id, b_id, date)
        col = "green" if "Thành công" in res or "Đã trả sách" in res else "red"
        self.lbl_msg_r.configure(text=res, text_color=col)

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)
        
    def change_db_mode(self, mode: str):
        self.db_mode = mode
        msgbox.showinfo("Cơ sở dữ liệu", f"Đã chuyển sang chế độ lưu trữ: {mode}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
