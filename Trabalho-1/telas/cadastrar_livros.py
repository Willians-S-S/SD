import tkinter as tk
from tkinter import messagebox
from crud import create_book

class CadastrarLivroScreen:
    def __init__(self, root, tela_anterior):
        self.root = root
        self.tela_anterior = tela_anterior
        self.frame = tk.Frame(root)
        self.frame.pack()

        # Campos para entrada de dados
        tk.Label(self.frame, text="Título:").pack()
        self.entry_title = tk.Entry(self.frame)
        self.entry_title.pack()

        tk.Label(self.frame, text="Autor:").pack()
        self.entry_author = tk.Entry(self.frame)
        self.entry_author.pack()

        tk.Label(self.frame, text="Páginas:").pack()
        self.entry_pages = tk.Entry(self.frame)
        self.entry_pages.pack()

        tk.Label(self.frame, text="Ano:").pack()
        self.entry_year = tk.Entry(self.frame)
        self.entry_year.pack()

        # Botão para cadastrar o livro
        tk.Button(self.frame, text="Cadastrar", command=self.add_book).pack()
        tk.Button(self.frame, text="Voltar", command=self.voltar).pack()

    def add_book(self):
        """Cadastra um novo livro no Firebase."""
        title = self.entry_title.get().strip()
        author = self.entry_author.get().strip()
        pages = self.entry_pages.get().strip()
        year = self.entry_year.get().strip()

        if not title or not author or not pages or not year:
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return

        try:
            # Converte páginas e ano para inteiros
            pages = int(pages)
            year = int(year)

            # Cria o livro no Firestore
            create_book(title, author, pages, year)
            messagebox.showinfo("Sucesso", "Livro cadastrado com sucesso!")
            self.frame.destroy()  # Fecha a tela após o cadastro
            
            from main import App  # Importe a classe principal
            app = App(self.root)
            app.show_books()
        except ValueError:
            messagebox.showerror("Erro", "Páginas e Ano devem ser números válidos.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar livro: {e}")

    def voltar(self):
        self.frame.destroy()
        if self.tela_anterior:
            self.tela_anterior.frame.pack()