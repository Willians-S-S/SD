# main.py
import tkinter as tk
# from login import LoginScreen
# from register import RegisterScreen
# from add_book import AddBookScreen
# from update_book import UpdateBookScreen
# from view_books import ViewBooksScreen
# from database import create_tables

def main():
    root = tk.Tk()
    root.title('Book Manager')
    root.geometry('400x400')

    # create_tables()

    login_screen = LoginScreen(root)
    login_screen.pack(fill='both', expand=True)

    root.mainloop()

if __name__ == '__main__':
    main()

# database.py
import sqlite3

def create_tables():
    conn = sqlite3.connect('books.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT UNIQUE,
                      password TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS books (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      title TEXT,
                      author TEXT)''')
    conn.commit()
    conn.close()

# login.py
class LoginScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        tk.Label(self, text='Login').pack()
        self.username = tk.Entry(self)
        self.username.pack()
        self.password = tk.Entry(self, show='*')
        self.password.pack()
        tk.Button(self, text='Login', command=self.login).pack()
        tk.Button(self, text='Register', command=self.go_to_register).pack()
    
    def login(self):
        print(f'Logging in with {self.username.get()}')
    
    def go_to_register(self):
        self.destroy()
        RegisterScreen(self.master).pack(fill='both', expand=True)

# register.py
class RegisterScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        tk.Label(self, text='Register').pack()
        self.username = tk.Entry(self)
        self.username.pack()
        self.password = tk.Entry(self, show='*')
        self.password.pack()
        tk.Button(self, text='Register', command=self.register_user).pack()
        tk.Button(self, text='Back', command=self.go_to_login).pack()
    
    def register_user(self):
        print(f'User {self.username.get()} registered!')
    
    def go_to_login(self):
        self.destroy()
        LoginScreen(self.master).pack(fill='both', expand=True)

# add_book.py
class AddBookScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        tk.Label(self, text='Add Book').pack()
        self.book_title = tk.Entry(self)
        self.book_title.pack()
        self.book_author = tk.Entry(self)
        self.book_author.pack()
        tk.Button(self, text='Add Book', command=self.add_book).pack()
    
    def add_book(self):
        print(f'Added book: {self.book_title.get()} by {self.book_author.get()}')

# update_book.py
class UpdateBookScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        tk.Label(self, text='Update Book').pack()
        self.book_id = tk.Entry(self)
        self.book_id.pack()
        self.new_title = tk.Entry(self)
        self.new_title.pack()
        self.new_author = tk.Entry(self)
        self.new_author.pack()
        tk.Button(self, text='Update Book', command=self.update_book).pack()
    
    def update_book(self):
        print(f'Updated book ID {self.book_id.get()} to {self.new_title.get()} by {self.new_author.get()}')

# view_books.py
class ViewBooksScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        tk.Label(self, text='Books List').pack()

# delete_book.py
def delete_book(book_id):
    print(f'Book with ID {book_id} deleted!')
