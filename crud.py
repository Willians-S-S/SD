import firebase_admin
from firebase_admin import credentials, firestore, auth

# Configurar Firebase
cred = credentials.Certificate("/home/will/Documentos/UFPI/SD/cred2.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Coleção de Usuários
USERS_COLLECTION = "users"

def create_user(name, email, password):
    """
    Cria um novo usuário no Firebase Authentication e salva os dados no Firestore.
    """
    user_record = auth.create_user(
            email=email,
            display_name=name,
            password=password
        )
        
        # Salvar dados adicionais no Firestore
    user_data = {
        "email": email,
        "display_name": name,
        "password": password  # OBS: Não é recomendado salvar senhas diretamente no Firestore
    }
    db.collection(USERS_COLLECTION).document(user_record.uid).set(user_data)
    
    print(f"Usuário '{name}' criado com sucesso!")
    # try:
    #     # Criar usuário no Firebase Authentication
    #     user_record = auth.create_user(
    #         email=email,
    #         display_name=name,
    #         password=password
    #     )
        
    #     # Salvar dados adicionais no Firestore
    #     user_data = {
    #         "email": email,
    #         "display_name": name,
    #         "password": password  # OBS: Não é recomendado salvar senhas diretamente no Firestore
    #     }
    #     db.collection(USERS_COLLECTION).document(user_record.uid).set(user_data)
        
    #     print(f"Usuário '{name}' criado com sucesso!")
    # except Exception as e:
    #     print(f"Erro ao criar usuário: {e}")

def read_users():
    """
    Lista todos os usuários salvos no Firestore.
    """
    try:
        users = db.collection(USERS_COLLECTION).stream()
        for user in users:
            print(f"{user.id}: {user.to_dict()}")
    except Exception as e:
        print(f"Erro ao listar usuários: {e}")

def read_user_by_id(user_id):
    """
    Lê os dados de um usuário específico pelo ID no Firestore.
    """
    try:
        user_ref = db.collection(USERS_COLLECTION).document(user_id)
        user = user_ref.get()
        
        if user.exists:
            print(user.to_dict())
        else:
            print(f"Usuário com ID '{user_id}' não encontrado.")
    except Exception as e:
        print(f"Erro ao ler usuário: {e}")

def update_user(user_id, field, new_value):
    """
    Atualiza um campo específico de um usuário no Firestore.
    """
    try:
        user_ref = db.collection(USERS_COLLECTION).document(user_id)
        user_ref.update({field: new_value})
        print(f"Usuário {user_id} atualizado!")
    except Exception as e:
        print(f"Erro ao atualizar usuário: {e}")

def delete_user(user_id):
    """
    Deleta um usuário específico do Firestore.
    """
    try:
        db.collection(USERS_COLLECTION).document(user_id).delete()
        print(f"Usuário {user_id} deletado!")
    except Exception as e:
        print(f"Erro ao deletar usuário: {e}")

def login_user(email, password):
    try:
        response_ref = db.collection(USERS_COLLECTION).where('email', '==', email).stream()
        
        for doc in response_ref:
            response = doc.reference
            id = doc.id
            break

        response = response.get().to_dict()
        
        if response["email"] == email and response["password"] == password:
            return id, response
        
        return False
       
    except Exception as e:
        print(f"Erro ao fazer login: {e}")



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
    list_book = []
    for book in books:
        dic_book = book.to_dict()
        dic_book["id"] = book.id    
        list_book.append(dic_book)
    
    return list_book

def update_book(book_id, field, new_value):
    book_ref = db.collection(BOOKS_COLLECTION).document(book_id)
    book_ref.update({field: new_value})
    print(f"Livro {book_id} atualizado!")

def delete_book(book_id):
    db.collection(BOOKS_COLLECTION).document(book_id).delete()
    print(f"Livro {book_id} deletado!")

if __name__ == "__main__":
    # Exemplos de uso das funções
    # create_user("João Silva", "joao@email.com", "senha123")
    # read_users()
    # read_user_by_id("AqnsIUHfWHTnVYI9E4lNHCQArjV2")
    # update_user("AqnsIUHfWHTnVYI9E4lNHCQArjV2", "display_name", "João da Silva")
    # delete_user("AqnsIUHfWHTnVYI9E4lNHCQArjV2")
    print(login_user("joao@email.com", "senha123"))
    # print(login_user("jo@email.com", "senha123"))
    pass

