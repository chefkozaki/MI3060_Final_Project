document.addEventListener('DOMContentLoaded', () => {
    // Theme toggler
    const themeToggle = document.getElementById('theme-toggle-btn');
    themeToggle.addEventListener('click', () => {
        document.body.classList.toggle('dark-theme');
        document.body.classList.toggle('light-theme');
    });

    // Sidebar toggler
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
    });

    // Tab navigation
    const navLinks = document.querySelectorAll('.nav-links li');
    const tabContents = document.querySelectorAll('.tab-content');

    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            navLinks.forEach(l => l.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            link.classList.add('active');
            document.getElementById(link.getAttribute('data-tab')).classList.add('active');
            
            // Reload data based on tab
            if(link.getAttribute('data-tab') === 'books-tab') loadBooks();
            if(link.getAttribute('data-tab') === 'readers-tab') loadReaders();
            if(link.getAttribute('data-tab') === 'borrow-tab') loadQueue();
        });
    });

    // Initial load
    loadBooks();
});

// Modal Logic
function showModal(id) {
    document.getElementById(id).style.display = 'flex';
}

function closeModal(id) {
    document.getElementById(id).style.display = 'none';
}

window.onclick = function(event) {
    if (event.target.className === 'modal') {
        event.target.style.display = "none";
    }
}

// Toast Logic
function showToast(message, isError = false) {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${isError ? 'error' : ''}`;
    toast.innerText = message;
    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// API Calls
const API_URL = '/api';
const ITEMS_PER_PAGE = 50;

let allBooks = [];
let booksCurrentPage = 1;
let allReaders = [];
let readersCurrentPage = 1;

async function fetchJSON(url, options = {}) {
    try {
        const response = await fetch(url, options);
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || 'Lỗi từ máy chủ');
        }
        return data;
    } catch (error) {
        showToast(error.message, true);
        throw error;
    }
}

// Book logic
async function loadBooks() {
    try {
        const books = await fetchJSON(`${API_URL}/books`);
        allBooks = books;
        renderBooksPage(1);
    } catch(e) {}
}

async function searchBook() {
    const val = document.getElementById('search-book-id').value.trim();
    if (!val) {
        loadBooks();
        return;
    }
    try {
        const res = await fetchJSON(`${API_URL}/books/search/${val}`);
        allBooks = [res];
        renderBooksPage(1);
    } catch(e) {
        allBooks = [];
        renderBooksPage(1);
    }
}
window.searchBook = searchBook;



window.renderBooksPage = function(page) {
    booksCurrentPage = page;
    const start = (page - 1) * ITEMS_PER_PAGE;
    const end = start + ITEMS_PER_PAGE;
    const pageBooks = allBooks.slice(start, end);

    const tbody = document.getElementById('books-tbody');
    let html = '';
    pageBooks.forEach(b => {
        const borrowedByText = b.borrowed_by && b.borrowed_by.length > 0 ? b.borrowed_by.join(', ') : 'Không có';
        html += `
            <tr>
                <td>${b.book_id}</td>
                <td>${b.title}</td>
                <td>${b.author}</td>
                <td>${b.stock}</td>
                <td>${borrowedByText}</td>
                <td>${b.total_quantity}</td>
                <td>
                    <button class="btn btn-secondary btn-sm" onclick="openEditBookModal('${b.book_id}', '${b.title.replace(/'/g, "\\'")}', '${b.total_quantity}', '${b.location || 'Chưa xác định'}')">Sửa</button>
                    <button class="btn btn-danger btn-sm" onclick="deleteBook('${b.book_id}')">Xóa</button>
                </td>
            </tr>
        `;
    });
    tbody.innerHTML = html;
    
    // Render pagination
    const totalPages = Math.ceil(allBooks.length / ITEMS_PER_PAGE) || 1;
    const pagContainer = document.getElementById('books-pagination');
    pagContainer.innerHTML = `
        <button class="btn btn-secondary btn-sm" onclick="renderBooksPage(${Math.max(1, page - 1)})" ${page === 1 ? 'disabled' : ''}>Trước</button>
        <span>Trang ${page} / ${totalPages}</span>
        <button class="btn btn-secondary btn-sm" onclick="renderBooksPage(${Math.min(totalPages, page + 1)})" ${page === totalPages ? 'disabled' : ''}>Sau</button>
    `;
}

function openEditBookModal(id, title, qty, location) {
    document.getElementById('edit-book-id').value = id;
    document.getElementById('edit-book-title').value = title;
    document.getElementById('edit-book-quantity').value = qty;
    document.getElementById('edit-book-location').value = location;
    showModal('edit-book-modal');
}

async function updateBook() {
    const id = document.getElementById('edit-book-id').value;
    const title = document.getElementById('edit-book-title').value;
    const qty = document.getElementById('edit-book-quantity').value;
    const location = document.getElementById('edit-book-location').value;

    try {
        const res = await fetchJSON(`${API_URL}/books/${id}`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({title, quantity: parseInt(qty), location})
        });
        showToast(res.message);
        closeModal('edit-book-modal');
        loadBooks();
    } catch(e) {}
}

async function addBook() {
    const id = document.getElementById('new-book-id').value;
    const title = document.getElementById('new-book-title').value;
    const author = document.getElementById('new-book-author').value;
    const qty = document.getElementById('new-book-quantity').value;

    try {
        const res = await fetchJSON(`${API_URL}/books`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({book_id: id, title, author, quantity: parseInt(qty)})
        });
        showToast(res.message);
        closeModal('add-book-modal');
        loadBooks();
    } catch(e) {}
}

async function deleteBook(id) {
    try {
        const res = await fetchJSON(`${API_URL}/books/${id}`, { method: 'DELETE' });
        showToast(res.message);
        loadBooks();
    } catch(e) {}
}

// Reader logic
async function loadReaders() {
    try {
        const readers = await fetchJSON(`${API_URL}/readers`);
        allReaders = readers;
        renderReadersPage(1);
    } catch(e) {}
}

async function searchReader() {
    const val = document.getElementById('search-reader-id').value.trim();
    if (!val) {
        loadReaders();
        return;
    }
    try {
        const res = await fetchJSON(`${API_URL}/readers/search/${val}`);
        allReaders = [res];
        renderReadersPage(1);
    } catch(e) {
        allReaders = [];
        renderReadersPage(1);
    }
}
window.searchReader = searchReader;



window.renderReadersPage = function(page) {
    readersCurrentPage = page;
    const start = (page - 1) * ITEMS_PER_PAGE;
    const end = start + ITEMS_PER_PAGE;
    const pageReaders = allReaders.slice(start, end);

    const tbody = document.getElementById('readers-tbody');
    let html = '';
    pageReaders.forEach(r => {
        const statusText = r.status === 1 ? 'Hoạt động' : 'Đã khóa';
        html += `
            <tr>
                <td>${r.reader_id}</td>
                <td>${r.name}</td>
                <td>${r.class_name}</td>
                <td>${statusText}</td>
                <td>
                    ${r.status === 1 ? `<button class="btn btn-danger btn-sm" onclick="lockReader('${r.reader_id}')">Khóa thẻ</button>` : ''}
                </td>
            </tr>
        `;
    });
    tbody.innerHTML = html;
    
    // Render pagination
    const totalPages = Math.ceil(allReaders.length / ITEMS_PER_PAGE) || 1;
    const pagContainer = document.getElementById('readers-pagination');
    pagContainer.innerHTML = `
        <button class="btn btn-secondary btn-sm" onclick="renderReadersPage(${Math.max(1, page - 1)})" ${page === 1 ? 'disabled' : ''}>Trước</button>
        <span>Trang ${page} / ${totalPages}</span>
        <button class="btn btn-secondary btn-sm" onclick="renderReadersPage(${Math.min(totalPages, page + 1)})" ${page === totalPages ? 'disabled' : ''}>Sau</button>
    `;
}

async function addReader() {
    const id = document.getElementById('new-reader-id').value;
    const name = document.getElementById('new-reader-name').value;
    const cls = document.getElementById('new-reader-class').value;

    try {
        const res = await fetchJSON(`${API_URL}/readers`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({reader_id: id, name, class_name: cls})
        });
        showToast(res.message);
        closeModal('add-reader-modal');
        loadReaders();
    } catch(e) {}
}

async function lockReader(id) {
    try {
        const res = await fetchJSON(`${API_URL}/readers/${id}/lock`, { method: 'POST' });
        showToast(res.message);
        loadReaders();
    } catch(e) {}
}

async function uploadReaders(event) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const res = await fetchJSON(`${API_URL}/upload/readers`, {
            method: 'POST',
            body: formData
        });
        showToast(res.message);
        loadReaders();
    } catch(e) {}
    event.target.value = ''; // reset
}

async function uploadBooks(event) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const res = await fetchJSON(`${API_URL}/upload/books`, {
            method: 'POST',
            body: formData
        });
        showToast(res.message);
        loadBooks();
    } catch(e) {}
    event.target.value = ''; // reset
}

async function resetDatabase() {
    if (!confirm("Bạn có chắc chắn muốn xóa toàn bộ dữ liệu sách và độc giả? Hành động này không thể hoàn tác!")) {
        return;
    }
    try {
        const res = await fetchJSON(`${API_URL}/reset`, { method: 'POST' });
        showToast(res.message);
        loadBooks();
        loadReaders();
        loadQueue();
    } catch(e) {}
}

// Borrow/Return Logic
async function borrowBook() {
    const reader_id = document.getElementById('borrow-reader-id').value;
    const book_id = document.getElementById('borrow-book-id').value;
    try {
        const res = await fetchJSON(`${API_URL}/borrow`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({reader_id, book_id})
        });
        showToast(res.message);
        loadQueue();
    } catch(e) {}
}

async function returnBook() {
    const reader_id = document.getElementById('return-reader-id').value;
    const book_id = document.getElementById('return-book-id').value;
    try {
        const res = await fetchJSON(`${API_URL}/return`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({reader_id, book_id})
        });
        showToast(res.message);
        loadQueue();
    } catch(e) {}
}

async function loadQueue() {
    try {
        const queue = await fetchJSON(`${API_URL}/queue`);
        const tbody = document.getElementById('queue-tbody');
        let html = '';
        queue.forEach(q => {
            html += `
                <tr>
                    <td>${q.reader_id}</td>
                    <td>${q.book_id}</td>
                </tr>
            `;
        });
        tbody.innerHTML = html;
    } catch(e) {}
}

// Dynamic info for Borrow/Return
function setupReaderLookup(inputId, displayId) {
    let timeoutId;
    document.getElementById(inputId)?.addEventListener('input', (e) => {
        clearTimeout(timeoutId);
        const val = e.target.value.trim();
        const display = document.getElementById(displayId);
        if (!val) { display.innerHTML = ''; return; }
        
        timeoutId = setTimeout(async () => {
            try {
                const res = await fetchJSON(`${API_URL}/readers/${val}/info`);
                let html = `<strong>${res.name}</strong> - Thẻ: ${res.status}`;
                if (res.borrowed_books && res.borrowed_books.length > 0) {
                    html += `<br>Sách đang mượn: ` + res.borrowed_books.map(b => `[${b.book_id}] ${b.title}`).join(', ');
                } else {
                    html += `<br>Chưa mượn sách nào.`;
                }
                display.innerHTML = html;
            } catch (error) {
                display.innerHTML = `<span style="color: var(--danger-color);">Không tìm thấy độc giả.</span>`;
            }
        }, 500);
    });
}

function setupBookLookup(inputId, displayId) {
    let timeoutId;
    document.getElementById(inputId)?.addEventListener('input', (e) => {
        clearTimeout(timeoutId);
        const val = e.target.value.trim();
        const display = document.getElementById(displayId);
        if (!val) { display.innerHTML = ''; return; }
        
        timeoutId = setTimeout(async () => {
            try {
                const res = await fetchJSON(`${API_URL}/books/${val}`);
                display.innerHTML = `<strong>${res.title}</strong> - Tồn kho: ${res.stock}`;
            } catch (error) {
                display.innerHTML = `<span style="color: var(--danger-color);">Không tìm thấy sách.</span>`;
            }
        }, 500);
    });
}

setupReaderLookup('borrow-reader-id', 'borrow-reader-info');
setupBookLookup('borrow-book-id', 'borrow-book-info');
setupReaderLookup('return-reader-id', 'return-reader-info');
setupBookLookup('return-book-id', 'return-book-info');
