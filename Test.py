import threading
import csv
import re
from datetime import datetime

class Book:
    def __init__(self, title, author, isbn, quantity_available):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.quantity_available = quantity_available

    def __str__(self):
        return f"{self.title} by {self.author} (ISBN: {self.isbn}) - Available: {self.quantity_available}"

class Borrower:
    def __init__(self, name, address):
        self.name = name
        self.address = address
        self.borrowed_books = []

    def __str__(self):
        return f"{self.name} ({self.address}) - Borrowed books: {len(self.borrowed_books)}"

def validate_isbn(isbn):
    # Simple ISBN validation using regular expression
    return re.match(r"^\d{3}-\d{10}$", isbn) is not None

def log_timestamp(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {func.__name__} executed.")
        return result
    return wrapper

class Library:
    def __init__(self):
        self.books = []
        self.borrowers = []
        self.lock = threading.Lock()

    def add_book(self, book):
        self.books.append(book)

    def add_borrower(self, borrower):
        self.borrowers.append(borrower)

    @log_timestamp
    def borrow_book(self, borrower, book):
        with self.lock:
            if book.quantity_available > 0:
                book.quantity_available -= 1
                borrower.borrowed_books.append(book)
                print(f"{borrower.name} borrowed {book.title}")
            else:
                print(f"Sorry, {book.title} is not available for borrowing.")

    @log_timestamp
    def return_book(self, borrower, book):
        with self.lock:
            if book in borrower.borrowed_books:
                book.quantity_available += 1
                borrower.borrowed_books.remove(book)
                print(f"{borrower.name} returned {book.title}")
            else:
                print(f"{borrower.name} did not borrow {book.title}")

    def average_books_per_borrower(self):
        total_books_borrowed = sum(len(borrower.borrowed_books) for borrower in self.borrowers)
        total_borrowers = len(self.borrowers)
        return total_books_borrowed / total_borrowers if total_borrowers > 0 else 0

    def save_inventory(self, filename):
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['Title', 'Author', 'ISBN', 'Quantity Available']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for book in self.books:
                writer.writerow({
                    'Title': book.title,
                    'Author': book.author,
                    'ISBN': book.isbn,
                    'Quantity Available': book.quantity_available
                })

    def save_borrowers(self, filename):
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['Name', 'Address', 'Borrowed Books']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for borrower in self.borrowers:
                writer.writerow({
                    'Name': borrower.name,
                    'Address': borrower.address,
                    'Borrowed Books': ', '.join([book.title for book in borrower.borrowed_books])
                })

    def load_inventory(self, filename):
        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                book = Book(
                    title=row['Title'],
                    author=row['Author'],
                    isbn=row['ISBN'],
                    quantity_available=int(row['Quantity Available'])
                )
                self.books.append(book)

    def load_borrowers(self, filename):
        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                borrower = Borrower(
                    name=row['Name'],
                    address=row['Address']
                )
                borrowed_books = row['Borrowed Books'].split(', ')
                for title in borrowed_books:
                    book = next((b for b in self.books if b.title == title), None)
                    if book:
                        borrower.borrowed_books.append(book)
                self.borrowers.append(borrower)

if __name__ == "__main__":
    # Instantiate a few book and borrower objects and add them to the library
    book1 = Book("The Catcher in the Rye", "J.D. Salinger", "123-4567890123", 5)
    book2 = Book("To Kill a Mockingbird", "Harper Lee", "456-7890123456", 3)

    borrower1 = Borrower("Alice", "123 Main St")
    borrower2 = Borrower("Bob", "456 Oak St")

    library = Library()
    library.add_book(book1)
    library.add_book(book2)
    library.add_borrower(borrower1)
    library.add_borrower(borrower2)

    # Borrow and return books
    library.borrow_book(borrower1, book1)
    library.return_book(borrower1, book1)

    # Calculate and print the average quantity of books borrowed per borrower
    avg_books_per_borrower = library.average_books_per_borrower()
    print(f"Average books per borrower: {avg_books_per_borrower}")

    # Save library inventory and borrower information to files
    library.save_inventory("inventory.csv")
    library.save_borrowers("borrowers.csv")

    # Load library inventory and borrower information from files
    library.load_inventory("inventory.csv")
    library.load_borrowers("borrowers.csv")

    # Simulate concurrent borrowing and returning of books by multiple borrowers using threading
    borrower3 = Borrower("Charlie", "789 Pine St")
    borrower4 = Borrower("David", "101 Cedar St")

    library.add_borrower(borrower3)
    library.add_borrower(borrower4)

    thread1 = threading.Thread(target=library.borrow_book, args=(borrower3, book1))
    thread2 = threading.Thread(target=library.borrow_book, args=(borrower4, book2))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    # Print the updated library status after concurrent operations
    print("\nUpdated Library Status:")
    library.average_books_per_borrower()
    for book in library.books:
        print(book)

    for borrower in library.borrowers:
        print(borrower)
