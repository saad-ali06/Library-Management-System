from random import random
from re import search
import threading
from threading import Lock
from csv import DictReader,DictWriter
import logging
from os.path import getsize,exists
import threading

#  Files_paths
inventory_file = 'inventory.csv'
borrowers_file = 'borrowers.csv'

# logger created and configured.
logging.basicConfig(level=logging.DEBUG,
                    filename="book_record.log",
                    filemode="w",
                    format="%(asctime)s %(name)s - %(levelname)s - %(message)s",
                    datefmt='%d-%b-%y %H:%M:%S')
logger1 = logging.getLogger(__name__)
foramtter = logging.Formatter("%(asctime)s %(name)s - %(levelname)s - %(message)s", datefmt='%y-%m-%d %H:%M:%S')
file_handler = logging.FileHandler("book_record.log", mode='w')
file_handler.setFormatter(foramtter)
file_handler.setLevel(logging.INFO)
logger1.addHandler(file_handler)
""" The stream Handler is to print on console"""
stream_handler = logging.StreamHandler()
logger1.addHandler(stream_handler)

def log_timestamp(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f"{func.__name__} executed.")
        return result
    return wrapper


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
This function down below are for file Erroe handling.
When open checks is file empty and path/dir exists
"""    
def is_file_empty_or_not_exists(file_path):
    if exists(file_path):
        return getsize(file_path) == 0
    else:
        print(f"The file {file_path} does not exist.")
        return None 

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
        self.borrowers_count = 0 
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
    
    # same ISBN so add in quantity of Book .    
    def append_book(self, book):
        for book1 in self.books:
            if book1.isbn == book.isbn:
                book1.quantity_available = book1.quantity_available + book.quantity_available

    
    @log_timestamp
    def borrow_book(self, borrower, book):
        self.lock.acquire()
        if book.quantity_available > 0:
            book.quantity_available -= 1
            borrower.borrowed_books.append(book)
            logger1.info(f"{borrower.name} borrowed {book.title}")
        else:
            print(f"Sorry, {book.title} is not available for borrowing.")
        self.lock.release()

    # Borrower returns the book.
    @log_timestamp
    def return_book(self, borrower, book):
        self.lock.acquire()
        
        if book in self.books:
            book.quantity_available += 1
            index_of_book = borrower.borrowed_books.index(book)
            # Remove book from borrower list.
            removed_book = borrower.borrowed_books.pop(index_of_book)
            logger1.info(f"{removed_book.title} Remove from {borrower.name}")
        else:
            print("The you are returning isn't ours Return.\nPlease return it where it belongs.  ")
        
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
                    'Type': book.type
                })


    # This func Load Data back to library Class Attributes.
    def load_book_inventory(self, filename):
        # This function return True if file empty or none if dir not exists.
        f = is_file_empty_or_not_exists(filename)
        if f or f==None:
            print("File is empty..\n Feilds are writed on File...")
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = ['Title', 'Author', 'ISBN', 'Quantity Available','Fiction','Type']
                writer = DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
            
        
        # main loading to file starts here.
        with open(filename, 'r') as csvfile:
            reader = DictReader(csvfile)
            for row in reader:
                if bool(row['Fiction']):
                    book = Fictional(
                        title=row['Title'],
                        author=row['Author'],
                        isbn=row['ISBN'],
                        quantity_available=int(row['Quantity Available']),
                        type = row['Type']
                    )
                else:
                    book = Nonfictional(
                        title=row['Title'],
                        author=row['Author'],
                        isbn=row['ISBN'],
                        quantity_available=int(row['Quantity Available']),
                        type = row['Type']
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
        # This function return True if file empty or none if dir not exists.
        f = is_file_empty_or_not_exists(filename)
        if f or f==None:
            print("File is empty..\n Feilds are writed on File...")
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = ['Name', 'Address', 'Borrowed Books']
                writer = DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
        
        
        # main loading to file starts here.
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
              
                
    def book_search_by_title(self,title=None):
        for book in self.books:
            if book.title == title:
                return (True,book)
        print
        return (False,None)    
                
    
    def book_search(self, isbn = None):
        if isvalid_isbn(isbn):
            for book in self.books:
                if isbn == book.isbn:
                    return (True,book)
        print("ISBN is invalid")
        return (False,None)
    
    def select_borrower(self, name):
        for borrower in self.borrowers:
            if name == borrower.name:
                return (True,borrower)
        print("Borrower not Found..")
        return (False,None)
    
    def borrowers_books(self):
        for borrower in self.borrowers:
            print(borrower.borrowed_books)
    
    
    # this finction simply show the books and there availablity.
    def display_books(self):
        f_books=[]
        nf_books=[]
        print("\n---------display Books----------")
        for book in self.books:
            if book.fiction == True:
                f_books.append(book)
            else:
                nf_books.append(book)
        print(""" Genre are display as For Romance: 1, Crime: 2, Comic: 3, Comedy: 4, Historic: 5, Horror: 6, Other: 7
                  Fictional Books are : """)        
        
        for f in f_books:
            print(f"Title = {f.title}; Auhtor = {f.author} ; Genre = {f.type}; Quantity = {f.quantity_available}")
        
        print(""" Genre are display as For Romance: 1, Crime: 2, Comic: 3, Comedy: 4, Historic: 5, Horror: 6, Other: 7
                  Non-Fictional Books are : """)
        for nf in nf_books:
            
            print(f"Title = {nf.title}; Auhtor = {nf.author} ; Genre = {nf.type}; Quantity = {nf.quantity_available}")
        print("------END-------")
    
    
    def display_borrowers(self):
        print("\n---------display Borrower----------")
        for borrower in self.borrowers:
            print(f'Borrower : {borrower.name} ')
            print("Borrowed Books are")
            for borrower_b in borrower.borrowed_books :
                print(f'Title {borrower_b.title} ')
        print("------END-------")
            
        
    """ 
    This function is not working properly so commented out.
    """    
    # def simple_search(self, type, fic=None):
    #     find_books = []
    #     find = False
    #     if fic == None:
    #         for book in self.books:
    #             if book.type == type:
    #                 find_books.append(book)
    #                 find = True
    #     elif fic:
    #         for book in self.books:
    #             if fic == book.fiction and type == book.type:
    #                 find_books.append(book)
    #                 find = True
    #     else:
    #         for book in self.books:
    #             if fic != book.fiction and type == book.type:
    #                 find_books.append(book)
    #                 find = True
    #     return find_books if find else None
     
     
library = Library()     
   
"""
This class going to help manage the main func which going to use adove classes.
repeatedly used code are combined into functions in Main class.
Define all the main functions like add, delete, borrow etc 
"""

class Main:
    # going to define all function like input, borrow etc.
    def input_book(self):
        try:
            #  title, author, isbn, quantity_available,type
            fic =  input("Enter Y/y For Fictional or any else for Non-Fictional(like N/n): ")
            fic = fic == "Y" or fic == "y"
            title = input("Enter Book Title: ")
            author = input("Enter Book author: ")
            isbn = input("Enter Book ISBN: ") 
            if isvalid_isbn(isbn):
                print("your ISBN verified and Accepted")
            else:
                print("ISBN is Incorret..")
                raise ValueError
            quantity_available = int(input("Enter Book quantity_available: "))
            type = int(input("""For Romance: 1, Crime: 2, Comic: 3, Comedy: 4, Historic: 5, Horror: 6, Other: 7
                         Enter Book Genre: """))
            if fic:
                return Fictional(title,author,isbn,quantity_available,type)
            else: 
                return Nonfictional(title,author,isbn,quantity_available,type)
        except Exception as e:
            print("---Wrong Input ---\n Case by: ",e)
        
       
    def input_borrower(self):

        name = input("Enter name of the Borrower: ")
        address = input("Enter Address of the Borrower: ")
        return Borrower(name,address) 
    
    def add_borrower(self, borrower):
        library.load_borrowers_data(borrowers_file)
        library.add_borrower(borrower=borrower)
        library.save_borrowers_data(borrowers_file)
    
    def add_booK(self,book):
        # Lock.acquire()
        library.load_book_inventory(inventory_file)
        library.add_book(book=book)
        library.save_book_inventory(inventory_file)
        # Lock.release()
        
if __name__ == "__main__" :
    print(""" 
              WELCOME TO LIBRARY MANAGEMENT SYSTEM>
              
              """)
    main = Main()

    a = input("Select Y/N for loading data from File..")
    if a=='Y' or a=='y':
        library.load_book_inventory(inventory_file)
        library.load_borrowers_data(borrowers_file)
    while True:
        # try:  with try program show value error so I commented it out.
            a = int(input(""" ---Select U choice---
                1 for add Book, 
                2 for add Borrower, 
                3 Display Books, 
                4 Display Borrowers  
                5 for borrow Book, 
                6 for return a Book, 
                7 for delete book,
                8 for multi borrow request,
                9 for multiple books return 
                """))
            if a == 1:
                library.load_book_inventory(inventory_file)
                book = main.input_book()
                library.add_book(book)
                library.save_book_inventory(inventory_file)
            elif a == 2:
                library.load_borrowers_data(borrowers_file)
                borrower = main.input_borrower()
                main.add_borrower(borrower)
                library.save_borrowers_data(borrowers_file)
                library.display_borrowers()
            elif a == 3:
                library.display_books()
            elif a == 4:
                library.display_borrowers()
            elif a == 5:
                library.display_borrowers()
                name = input("Select a Borrower by input his/her name: ")
                b,borrower = library.select_borrower(name)
                if b:
                    library.display_books()
                    book_title = input("Enter Book Title : ")
                    c,book=library.book_search_by_title(title=book_title)
                    if c:
                        library.borrow_book(borrower=borrower,book=book)
                    else:
                        print("Book not Found..")
                else:
                    print("Borrower not found..")
                
            elif a == 6:
                library.display_borrowers()
                name = input("Select a Borrower by input his/her name: ")
                b,borrower = library.select_borrower(name)
                if b:
                    library.borrowers_books()
                    book_title = input("Enter Book Title : ")
                    c,book=library.book_search_by_title(title=book_title)
                    if c:
                        library.return_book(borrower=borrower,book=book)
                    else:
                        print("Book not Found..")
                else:
                    print("Borrower not found..")
            elif a == 7:
                book_title = input("Enter Book Title : ")
                c,book=library.book_search_by_title(title=book_title)
                if c:
                    library.del_book(book=book)
                    library.save_book_inventory(inventory_file)
                    print('Book deleted')
                else:
                    print("Book not Found..")
            
            elif a == 8:
                library.load_book_inventory(inventory_file)
                library.load_borrowers_data(borrowers_file)
                library.display_borrowers()
                name = input("Select a Borrower by input his/her name: ")
                b,borrower = library.select_borrower(name)
                if b:
                    value = int(input("How many Book do u want to borrow"))
                    i = 0
                    threads = []
                    while i<value:
                        library.display_books()
                        book_title = input("Enter Book Title : ")
                        c,book=library.book_search_by_title(title=book_title)
                        if c:
                            thread = threading.Thread(target=library.borrow_book, args=(borrower, book))
                            threads.append(thread)
                            thread.start()
                        else:
                            print("Book not Found..")
                        i+=1
                        for thread in threads:
                            thread.join()
                        library.save_book_inventory(inventory_file)
                        library.save_borrowers_data(borrowers_file)
                    
                else:
                    print("Borrower not found")
            
            elif a == 9:
                library.load_book_inventory(inventory_file)
                library.load_borrowers_data(borrowers_file)
                library.display_borrowers()
                name = input("Select a Borrower by input his/her name: ")
                b,borrower = library.select_borrower(name)
                if b:
                    value = int(input("How many Book do u want to Reuturn"))
                    i = 0
                    threads = []
                    while i<value:
                        library.borrowers_books()
                        book_title = input("Enter Book Title : ")
                        c,book=library.book_search_by_title(title=book_title)
                        if c:
                            thread = threading.Thread(target=library.return_book, args=(borrower, book))
                            threads.append(thread)
                            thread.start()
                        else:
                            print("Book not Found..")
                        i+=1
                    for thread in threads:
                        thread.join()
                    
                else:
                    print("Borrower not found")
                
                    
        # except Exception as e:
        #     print(f"Program Crashed Because of :\n{e}")
        #     break
        
    """ Below comment are for checking different function error.."""
    
    # # book = main.input_book()
    # # library.add_book(book)
    # # library.save_book_inventory(inventory_file)
    # library.load_book_inventory(inventory_file)
    # library.load_borrowers_data(borrowers_file)
    # for book in library.books:
    #     print(book.title,type(book.fiction))
    
    # # book = main.input_book()
    # # if library.book_search(isbn=book.isbn):
    # #     library.append_book(book)
    # #     library.save_book_inventory(inventory_file)
    # # else:
    # #     library.add_book(book)
    # #     library.save_book_inventory(inventory_file)
        
    # # library.display_books()
    # # library.display_borrowers()
    
    # # library.del_book(book)
    
    # # library.display_books()
    # # library.display_borrowers()
    
    # # borrower = main.input_borrower()
    # # main.add_borrower(borrower)
    # # library.display_borrowers()
    
    # book1 = Fictional("The Catcher in the Rye", "J.D. Salinger", "123-4-5678", 5,2)
    # book2 = Nonfictional("To Kill a Mockingbird", "Harper Lee", "456-7-8901", 3,5)

    # borrower1 = Borrower("Aizaz", "123 Main St")
    # borrower2 = Borrower("Amar", "456 Oak St")
    # library.display_books()
    # library.display_borrowers()
    
    # library.borrow_book(borrower1, book1)
    
    # library.display_books()
    # library.display_borrowers()
    
    # library.return_book(borrower1, book1)
    
    # library.display_books()
    # library.display_borrowers()
    