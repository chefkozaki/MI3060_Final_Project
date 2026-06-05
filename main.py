from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import uvicorn
from library_logic import LibraryManager, FileDatabaseContext
from datetime import datetime

app = FastAPI(title="Library Management System API")

# Initialize Library Manager
manager = LibraryManager()

# Preload data if files exist
BOOKS_FILE = "books.txt"
READERS_FILE = "readers.txt"

# If files don't exist, create some mock data for testing
if not os.path.exists(BOOKS_FILE):
    with open(BOOKS_FILE, "w", encoding="utf-8") as f:
        f.write("B001,Cấu trúc dữ liệu và giải thuật,Nguyễn Văn A,5\n")
        f.write("B002,Lập trình C++ cơ bản,Trần Thị B,3\n")

if not os.path.exists(READERS_FILE):
    with open(READERS_FILE, "w", encoding="utf-8") as f:
        f.write("R001,Lê Văn C,IT1\n")
        f.write("R002,Phạm Thị D,IT2\n")

db_context = FileDatabaseContext(BOOKS_FILE, READERS_FILE)
db_context.load_books(manager)
db_context.load_readers(manager)

class BookCreate(BaseModel):
    book_id: str
    title: str
    author: str
    quantity: int

class BookUpdate(BaseModel):
    title: str | None = None
    quantity: int | None = None
    location: str | None = None

class ReaderCreate(BaseModel):
    reader_id: str
    name: str
    class_name: str

class BorrowRequest(BaseModel):
    book_id: str
    reader_id: str

class ReturnRequest(BaseModel):
    book_id: str
    reader_id: str

@app.get("/api/books")
def get_books():
    return manager.get_all_books()

@app.get("/api/books/{book_id}")
def get_book(book_id: str):
    book = manager.book_tree.search(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Sách không tồn tại")
    return {"title": book.title, "stock": book.stock}

@app.post("/api/upload/books")
async def upload_books(file: UploadFile = File(...)):
    contents = await file.read()
    text = contents.decode("utf-8")
    count = 0
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(',')
        if len(parts) >= 4:
            book_id = parts[0]
            quantity = int(parts[-1])
            author = parts[-2]
            title = ','.join(parts[1:-2])
            manager.add_book(book_id, title, author, quantity)
            count += 1
    return {"message": f"Đã nạp {count} cuốn sách từ file."}

@app.post("/api/books")
def add_book(book: BookCreate):
    success, msg = manager.add_book(book.book_id, book.title, book.author, book.quantity)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}

@app.put("/api/books/{book_id}")
def update_book(book_id: str, book: BookUpdate):
    success, msg = manager.update_book(book_id, title=book.title, quantity=book.quantity, location=book.location)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}

@app.delete("/api/books/{book_id}")
def delete_book(book_id: str):
    success, msg = manager.delete_book(book_id)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}

@app.get("/api/readers")
def get_readers():
    return manager.get_all_readers()

@app.get("/api/readers/{reader_id}/info")
def get_reader_info(reader_id: str):
    reader = manager.reader_tree.search(reader_id)
    if not reader:
        raise HTTPException(status_code=404, detail="Độc giả không tồn tại")
    
    status_text = "Hoạt động" if reader.status == 1 else "Đã khóa"
    
    borrowed_books = []
    # traverse DLL backwards (from tail to head) or head to tail
    # history_list has head and next, wait, DLLNode has next and prev
    current = reader.history_list.head
    while current:
        if current.data.status == "Borrowed":
            book = manager.book_tree.search(current.data.book_id)
            title = book.title if book else "Không xác định"
            borrowed_books.append({"book_id": current.data.book_id, "title": title})
        current = current.next
        
    return {
        "name": reader.name,
        "status": status_text,
        "borrowed_books": borrowed_books
    }

@app.post("/api/upload/readers")
async def upload_readers(file: UploadFile = File(...)):
    contents = await file.read()
    text = contents.decode("utf-8")
    count = 0
    for line in text.splitlines():
        parts = line.strip().split(',')
        if len(parts) >= 3:
            manager.add_reader(parts[0], parts[1], parts[2])
            count += 1
    return {"message": f"Đã nạp {count} độc giả từ file."}

@app.post("/api/readers")
def add_reader(reader: ReaderCreate):
    success, msg = manager.add_reader(reader.reader_id, reader.name, reader.class_name)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}

@app.post("/api/readers/{reader_id}/lock")
def lock_reader(reader_id: str):
    success, msg = manager.lock_reader(reader_id)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}

@app.post("/api/borrow")
def borrow_book(req: BorrowRequest):
    date_str = datetime.now().strftime("%Y-%m-%d")
    success, msg = manager.handle_borrow_book(req.book_id, req.reader_id, date_str)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}

@app.post("/api/return")
def return_book(req: ReturnRequest):
    date_str = datetime.now().strftime("%Y-%m-%d")
    success, msg = manager.handle_return_book(req.book_id, req.reader_id, date_str)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}

@app.get("/api/queue")
def get_queue():
    return manager.get_wait_queue_list()

@app.post("/api/reset")
def reset_database():
    global manager
    manager = LibraryManager()
    with open(BOOKS_FILE, "w", encoding="utf-8") as f:
        pass
    with open(READERS_FILE, "w", encoding="utf-8") as f:
        pass
    return {"message": "Cơ sở dữ liệu đã được làm rỗng thành công."}

# Mount frontend
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
