import tkinter as tk
from tkinter import messagebox
from crud import read_books, delete_book
from telas.atualizar_livros import AtualizarLivroScreen

class ListarLivrosScreen:
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(root)
        self.frame.pack()
        self.carregar_livros()

    def carregar_livros(self):
        try:
            livros = read_books()
            if not livros:
                messagebox.showinfo("Aviso", "Nenhum livro encontrado.")
                return

            for i, livro in enumerate(livros):
                tk.Label(self.frame, text=livro['title']).grid(row=i, column=0)
                tk.Label(self.frame, text=livro['author']).grid(row=i, column=1)
                tk.Button(self.frame, text="Editar", command=lambda id=livro['id']: self.editar_livro(id)).grid(row=i, column=2)
                tk.Button(self.frame, text="Deletar", command=lambda id=livro['id']: self.deletar_livro(id)).grid(row=i, column=3)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao listar livros: {e}")

    def editar_livro(self, book_id):
        self.frame.destroy()
        AtualizarLivroScreen(self.root, book_id)

    def deletar_livro(self, book_id):
        resposta = messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir este livro?")
        if resposta:
            try:
                delete_book(book_id)
                messagebox.showinfo("Sucesso", "Livro deletado com sucesso!")
                self.frame.destroy()
                self.__init__(self.root)  # Recarrega a tela
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao deletar livro: {e}")