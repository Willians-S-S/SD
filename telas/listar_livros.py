import tkinter as tk
from tkinter import messagebox
from telas.atualizar_livros import AtualizarLivroScreen
from telas.cadastrar_livros import CadastrarLivroScreen  # Importe a tela de cadastro de livros
from crud import read_books, delete_book  # Use a função correta do CRUD de livros

class ListarLivrosScreen:
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(root)
        self.frame.pack()
        self.carregar_livros()

    def carregar_livros(self):
        """Carrega a lista de livros do Firebase e exibe na tela."""
        try:
            livros = read_books()  # Obtém os livros do Firestore
            if not livros:
                messagebox.showinfo("Aviso", "Nenhum livro encontrado.")
                return

            # Limpa a tela antes de recarregar os livros
            for widget in self.frame.winfo_children():
                widget.destroy()

            # Exibe os livros em uma grade
            tk.Label(self.frame, text="Título", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=5, pady=5)
            tk.Label(self.frame, text="Autor", font=("Arial", 12, "bold")).grid(row=0, column=1, padx=5, pady=5)
            tk.Label(self.frame, text="Páginas", font=("Arial", 12, "bold")).grid(row=0, column=2, padx=5, pady=5)
            tk.Label(self.frame, text="Ano", font=("Arial", 12, "bold")).grid(row=0, column=3, padx=5, pady=5)

            for i, livro in enumerate(livros, start=1):
                tk.Label(self.frame, text=livro['title']).grid(row=i, column=0, padx=5, pady=2)
                tk.Label(self.frame, text=livro['author']).grid(row=i, column=1, padx=5, pady=2)
                tk.Label(self.frame, text=livro['pages']).grid(row=i, column=2, padx=5, pady=2)
                tk.Label(self.frame, text=livro['year']).grid(row=i, column=3, padx=5, pady=2)
                tk.Button(self.frame, text="Editar", command=lambda id=livro['id']: self.editar_livro(id)).grid(row=i, column=4, padx=5, pady=2)
                tk.Button(self.frame, text="Deletar", command=lambda id=livro['id']: self.deletar_livro(id)).grid(row=i, column=5, padx=5, pady=2)

            # Adiciona o botão para cadastrar um novo livro
            btn_cadastrar = tk.Button(self.frame, text="Cadastrar Livro", command=self.cadastrar_livro)
            btn_cadastrar.grid(row=len(livros) + 1, column=0, columnspan=6, pady=10)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao listar livros: {e}")

    def editar_livro(self, book_id):
        """Abre a tela de edição para o livro com o ID fornecido."""
        self.frame.destroy()
        AtualizarLivroScreen(self.root, book_id)

    def deletar_livro(self, book_id):
        """Deleta um livro pelo ID."""
        resposta = messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir este livro?")
        if resposta:
            try:
                delete_book(book_id)  # Deleta o livro no Firestore
                messagebox.showinfo("Sucesso", "Livro deletado com sucesso!")
                self.carregar_livros()  # Recarrega a lista de livros
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao deletar livro: {e}")

    def cadastrar_livro(self):
        """Abre a tela de cadastro de livros."""
        self.frame.destroy()
        CadastrarLivroScreen(self.root)