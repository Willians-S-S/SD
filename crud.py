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
    

def read_users():
    """
    Lista todos os usuários salvos no Firestore.
    """
    try:
        users = db.collection(USERS_COLLECTION).stream()
        user_list = []
        for user in users:
            user_dic = user.to_dict()
            user_dic["id"] = user.id
            user_list.append(user_dic)
        
        return user_list
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
            return user.to_dict()
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
        users_ref = db.collection(USERS_COLLECTION).where('email', '==', email).limit(1).stream()
        user_docs = list(users_ref)
        
        if not user_docs:
            return False
        
        user_doc = user_docs[0]
        user_data = user_doc.to_dict()
        
        if user_data['password'] != password:
            return False
        
        # Retorna o ID do documento e os dados
        return (user_doc.id, user_data)
    except Exception as e:
        print(f"Erro no login: {e}")
        return False


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

livros_exemplo = [
    {"title": "Dom Casmurro", "author": "Machado de Assis", "pages": 256, "year": 1899},
    {"title": "O Cortiço", "author": "Aluísio Azevedo", "pages": 320, "year": 1890},
    {"title": "Memórias Póstumas de Brás Cubas", "author": "Machado de Assis", "pages": 288, "year": 1881},
    {"title": "Vidas Secas", "author": "Graciliano Ramos", "pages": 208, "year": 1938},
    {"title": "Capitães da Areia", "author": "Jorge Amado", "pages": 224, "year": 1937},
    {"title": "O Guarani", "author": "José de Alencar", "pages": 304, "year": 1857},
    {"title": "Iracema", "author": "José de Alencar", "pages": 192, "year": 1865},
    {"title": "A Hora da Estrela", "author": "Clarice Lispector", "pages": 128, "year": 1977},
    {"title": "O Crime do Padre Amaro", "author": "Eça de Queirós", "pages": 416, "year": 1875},
    {"title": "Cem Anos de Solidão", "author": "Gabriel García Márquez", "pages": 448, "year": 1967},
]

# Função para criar os livros no Firestore
def criar_livros_exemplo():
    for livro in livros_exemplo:
        create_book(
            title=livro["title"],
            author=livro["author"],
            pages=livro["pages"],
            year=livro["year"]
        )



if __name__ == "__main__":
    # Exemplos de uso das funções
    # create_user("João Silva", "joao@email.com", "senha123")
    # read_users()
    # read_user_by_id("AqnsIUHfWHTnVYI9E4lNHCQArjV2")
    # update_user("AqnsIUHfWHTnVYI9E4lNHCQArjV2", "display_name", "João da Silva")
    # delete_user("AqnsIUHfWHTnVYI9E4lNHCQArjV2")
    # print(login_user("joao@email.com", "senha123"))
    # print(login_user("jo@email.com", "senha123"))
    criar_livros_exemplo()
    pass

