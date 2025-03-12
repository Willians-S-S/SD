import firebase_admin
from firebase_admin import credentials, firestore, auth


# Configurar Firebase
cred = credentials.Certificate("caminho/para/seu/arquivo.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Coleções
BOOKS_COLLECTION = "books"
USERS_COLLECTION = "users"

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

def create_user(username, name, email, password):
    user_record = auth.create_user(
        email=email,
        password=password,
        display_name=name
    )
    user_data = {
        "username": username,
        "name": name,
        "email": email
    }
    db.collection(USERS_COLLECTION).document(user_record.uid).set(user_data)
    print(f"Usuário '{username}' criado com sucesso!")

def login_user(email, password):
    # Firebase Authentication não permite login diretamente pelo SDK do Admin
    print("Autenticação deve ser feita pelo cliente usando Firebase Authentication SDK.")

if __name__ == "__main__":
    # Exemplos de uso
    create_book("Dom Casmurro", "Machado de Assis", 256, 1899)
    read_books()
    book_id = input("Digite o ID do livro para atualizar: ")
    update_book(book_id, "pages", 300)
    delete_book(book_id)
    
    # Criar usuário
    create_user("usuario1", "João Silva", "joao@email.com", "senha123")
