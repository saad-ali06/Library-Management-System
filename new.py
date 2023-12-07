from random import random
from re import search
import threading
from csv import DictReader,DictWriter

"""
The International Standard Book Number (ISBN) is a 13-digit number that 
uniquely identifies books and book-like products published internationally.
example:  "123-0-1234" 
In our case we are using this example for ISBN
"""
def isvalid_isbn(isbn):
    # Regural Expression for finding pattern.
    pattern = r'\d{3}\-\d\-\d{4}'
    # returns True if Find Pattern else False.
    return search(pattern=pattern,string=isbn) is not None
         

"""
In our case isbn_number_generator() function is not in use
added in case of future need. 
This function Generate and return ISBN number
For Examaple: "123-0-1234"
"""
def isbn_number_generator():
    isbn = ''
    for _ in range(1,10):
        number = random(0,9)
        isbn = isbn + str(number)
    isbn = isbn[0:3]+'-'+isbn[3]+'-'+isbn[5:]
    return isbn
    

""" 
Book Attributes: title, author, isbn, quantity_available  
"""
class Book:
    def __init__(self, title, author, isbn, quantity_available):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.quantity_available = quantity_available
   
    # When print() Book object/instance this Function will run.
    def __str__(self):
        return f"{self.title} by {self.author} (ISBN: {self.isbn}) - Available: {self.quantity_available}"


""" 
Sub-Class of Book Can add type(variable) on Book Class.
But this help us in Seaching
"""
class Fictional(Book):
    # add an addition variable which store Book type.(like: comic, sci-fi, romantic, educational etc)
    def __init__(self, title, author, isbn, quantity_available,type):
        self.type = type
        # add fiction variable help store and retrieve Book.
        self.fiction = True
        super().__init__(title, author, isbn, quantity_available)


""" 
Same as above.
Sub-Class of Book. Can add type(variable) on Book Class.
"""
class Nonfictional(Book):
    # add an addition variable which store Book type.(like: comic, sci-fi, romantic, educational etc)
    def __init__(self, title, author, isbn, quantity_available,type):
        self.type = type
        # add fiction variable help store and retrieve Book.
        self.fiction = False
        super().__init__(title, author, isbn, quantity_available)
        

""" 
Borrower Attributes: name, address, borrowed_books
"""
class Borrower:
    def __init__(self, name, address):
        self.name = name
        self.address = address
        self.borrowed_books = []

    def __str__(self):
        return f"{self.name} ({self.address}) - Borrowed books: {len(self.borrowed_books)}" 

""" 
Library Class 
func: add book, remove book, update inventor(add, remove), update borrowers(add, remove) 
"""
class Library:
    
    #Library Class Attributes
    def __init__(self):
        self.books = []
        self.borrowers = []
        self.lock = threading.Lock()

    # add Book to Library.
    def add_book(self, book):
        self.books.append(book)
    
    # delete Book from Library.    
    def del_book(self, book):
        if book in self.books:
            index_of_book =self.books.index(book)
            # Remove the element at the found index
            removed_book = self.books.pop(index_of_book)

            print(f"Removed Book: {removed_book.title}")
        
    # add Book to Borrower
    def add_borrower(self, borrower):
        self.borrowers.append(borrower)

    # @log_timestamp
    def borrow_book(self, borrower, book):
        self.lock.acquire()
        if book.quantity_available > 0:
            book.quantity_available -= 1
            borrower.borrowed_books.append(book)
            print(f"{borrower.name} borrowed {book.title}")
        else:
            print(f"Sorry, {book.title} is not available for borrowing.")
        self.lock.release()

    # Borrower returns the book.
    # @log_timestamp
    def return_book(self, borrower, book):
        self.lock.acquire()
        
        book.quantity += 1
        index_of_book = borrower.borrowed_books.index(book)
        # Remove book from borrower list.
        removed_book = borrower.borrowed_books.pop(index_of_book)
        print(f"{removed_book.title} Remove from {borrower.name}")
        
        self.lock.release()
        
    
    # Return a number how many borrowed by borrower.
    def average_books_per_borrower(self):
        total_books_borrowed = sum(len(borrower.borrowed_books) for borrower in self.borrowers)
        total_borrowers = len(self.borrowers)
        return total_books_borrowed / total_borrowers if total_borrowers > 0 else 0


    # This func Saves Book Data into csv File using Dictionary.
    def save_book_inventory(self, filename):
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['Title', 'Author', 'ISBN', 'Quantity Available','Fiction','Type']
            writer = DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for book in self.books:
                writer.writerow({
                    'Title': book.title,
                    'Author': book.author,
                    'ISBN': book.isbn,
                    'Quantity Available': book.quantity_available,
                    'Fiction': book.fiction,
                    'Tpye': book.type
                })


    # This func Load Data back to library Class Attributes.
    def load_book_inventory(self, filename):
        with open(filename, 'r') as csvfile:
            reader = DictReader(csvfile)
            for row in reader:
                book = Book(
                    title=row['Title'],
                    author=row['Author'],
                    isbn=row['ISBN'],
                    quantity_available=int(row['Quantity Available']),
                    fiction = bool(row['Fiction']),
                    type = row['type']
                )
                self.books.append(book)        


    # This Function Saves Borrowers Data
    def save_borrowers_data(self, filename):
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['Name', 'Address', 'Borrowed Books']
            writer = DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for borrower in self.borrowers:
                writer.writerow({
                    'Name': borrower.name,
                    'Address': borrower.address,
                    # A Borrower Borrowed a list of Books so Saving Accordingly.
                    'Borrowed Books': ':- '.join([book.title for book in borrower.borrowed_books])
                })

    
    # This Function Loads Borrowers Data
    def load_borrowers_data(self, filename):
        with open(filename, 'r') as csvfile:
            reader = DictReader(csvfile)
            for row in reader:
                borrower = Borrower(
                    name=row['Name'],
                    address=row['Address']
                )
                # Borrowed Books data saved in a row separated by ":- "
                borrowed_books = row['Borrowed Books'].split(':- ')
                for title in borrowed_books:
                    book = next((b for b in self.books if b.title == title), None)
                    if book:
                        borrower.borrowed_books.append(book)
                self.borrowers.append(borrower)
              
                
    def book_search(self,title=None):
        find_book = []
        find = False
        for book in self.books:
            if book.title == title:
                find_book.append(book)
                find = True
        return find_book if find else None
                
    
    def book_search(self, isbn = None):
        if isvalid_isbn(isbn):
            for book in self.books:
                if isbn == book.isbn:
                    return book
            print("ISBN is invalid")
            return None
        
        
    def simple_search(self, type, fic=None):
        find_books = []
        find = False
        if fic == None:
            for book in self.books:
                if book.type == type:
                    find_books.append(book)
                    find = True
        elif fic:
            for book in self.books:
                if fic == book.fiction and type == book.type:
                    find_books.append(book)
        else:
            for book in self.books:
                if fic != book.fiction and type == book.type:
                    find_books.append(book)
            
                    
                
        

"""
This class going to help manage the main func which going to use adove classes.
repeatedly used code are combined into functions in Main class.
Define all the main functions like add, delete, borrow etc 
"""
class Main:
    # going to define all function like add,delete, borrow etc.
    pass  

  