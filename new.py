from random import random
from re import search


"""
The International Standard Book Number (ISBN) is a 13-digit number that 
uniquely identifies books and book-like products published internationally.
example:  "123-0-1234" 
In our case we are using this example for ISBN
"""
def isvalid_isbn(isbn):
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

    def __str__(self):
        return f"{self.title} by {self.author} (ISBN: {self.isbn}) - Available: {self.quantity_available}"


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
This class going to help manage the main func which going to use adove classes.
repeatedly used code are combined into functions in Main class.
Define all the main functions like add, delete, borrow etc 
"""
class Main:
    # going to define all function like add,delete, borrow etc.
    pass  

  