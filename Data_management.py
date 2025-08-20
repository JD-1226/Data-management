class Book:
    def __init__(self, title, author, isbn, available=True):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.available = available
        self.borrower = None

    def __str__(self):
        status = "Available" if self.available else "Not Available"
        return f"{self.title} by {self.author} (ISBN: {self.isbn}) - {status}"


class User:
    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name
        self.books_borrowed = []

    def __str__(self):
        return f"User: {self.name} (ID: {self.user_id}) - Books borrowed: {len(self.books_borrowed)}"

    def return_all_books(self, library):
        count = 0
        for book in self.books_borrowed:
            book.available = True
            book.borrower = None
            count += 1
        self.books_borrowed.clear()
        return count


class Library:
    def __init__(self):
        self.books = []
        self.users = []

    def add_book(self, book):
        self.books.append(book)

    def add_user(self, user):
        self.users.append(user)

    def borrow_book(self, book_isbn, user_id):
        book = next((b for b in self.books if b.isbn == book_isbn), None)
        if not book:
            return "Book not found"
        user = next((u for u in self.users if u.user_id == user_id), None)
        if not user:
            return "User not found"
        if not book.available:
            return "Book is not available"
        book.available = False
        book.borrower = user
        user.books_borrowed.append(book)
        return "Book borrowed successfully"

    def search_by_title(self, title):
        search_term = title.lower()
        return [book for book in self.books if search_term in book.title.lower()]

    def get_statistics(self):
        total_books = len(self.books)
        available_books = sum(1 for book in self.books if book.available)
        borrowed_books = total_books - available_books
        total_users = len(self.users)
        users_with_books = sum(1 for user in self.users if user.books_borrowed)
        return {
            "total_books": total_books,
            "available_books": available_books,
            "borrowed_books": borrowed_books,
            "total_users": total_users,
            "users_with_books": users_with_books
        } 
    

library = Library()

library.add_book(Book("The Hobbit", "J.R.R. Tolkien", "12345"))
library.add_book(Book("1984", "George Orwell", "67890"))

library.add_user(User(1, "Alice"))
library.add_user(User(2, "Bob"))

print(library.borrow_book("12345", 1))  
print(library.borrow_book("67890", 2))  
print(library.borrow_book("11111", 1))
