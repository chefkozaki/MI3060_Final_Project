import random

def generate_data():
    # Generate 10000 books
    with open('books.txt', 'w', encoding='utf-8') as f:
        # Format: book_id,title,author,stock
        for i in range(1, 10001):
            book_id = f"B{i:05d}"
            title = f"Book Title {i}"
            author = f"Author {i}"
            stock = random.randint(1, 50)
            f.write(f"{book_id},{title},{author},{stock}\n")
    
    print("Generated books.txt with 10000 records.")

    # Generate 10000 readers
    classes = ["CS101", "CS102", "SE201", "SE202", "IT301", "IT302"]
    with open('readers.txt', 'w', encoding='utf-8') as f:
        # Format: reader_id,name,class_name,is_locked
        for i in range(1, 10001):
            reader_id = f"R{i:05d}"
            name = f"Reader Name {i}"
            class_name = random.choice(classes)
            is_locked = "False"
            f.write(f"{reader_id},{name},{class_name},{is_locked}\n")
            
    print("Generated readers.txt with 10000 records.")

if __name__ == "__main__":
    generate_data()
