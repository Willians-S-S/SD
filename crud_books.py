import firebase_admin
from firebase_admin import credentials, firestore, auth


cred = credentials.Certificate("/home/will/Documentos/UFPI/SD/cred.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

BOOKS_COLLECTION = "books"

def create_book(title, author, pages, year):
    book_data = {
        "title": title,
        "author": author,
        "pages": pages,
        "year": year
    }
    doc_ref = db.collection(BOOKS_COLLECTION).add(book_data)
    print(f"Livro '{title}' adicionado com ID: {doc_ref[1].id}")

def read_books():
    books = db.collection(BOOKS_COLLECTION).stream()
    for book in books:
        print(f"{book.id}: {book.to_dict()}")

def update_book(book_id, field, new_value):
    book_ref = db.collection(BOOKS_COLLECTION).document(book_id)
    book_ref.update({field: new_value})
    print(f"Livro {book_id} atualizado!")

def delete_book(book_id):
    db.collection(BOOKS_COLLECTION).document(book_id).delete()
    print(f"Livro {book_id} deletado!")

if __name__ == "__main__":
    # Exemplos de uso
    create_book("Dom Casmurro", "Machado de Assis", 256, 1899)
    read_books()
    # book_id = input("Digite o ID do livro para atualizar: ")
    # update_book(book_id, "pages", 300)
    # delete_book(book_id)
    
    # Criar usuário
    # create_user("João Silva", "joao@email.com", "senha123")
