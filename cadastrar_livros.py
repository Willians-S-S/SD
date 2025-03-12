import tkinter as tk
from tkinter import messagebox
# from database import adicionar_livro

class CadastrarLivroScreen:
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(root)
        self.frame.pack()

        # Labels e Entrys para título, autor, ano, etc.
        self.label_titulo = tk.Label(self.frame, text="Título:")
        self.label_titulo.pack()
        self.entry_titulo = tk.Entry(self.frame)
        self.entry_titulo.pack()

        self.label_autor = tk.Label(self.frame, text="Autor:")
        self.label_autor.pack()
        self.entry_autor = tk.Entry(self.frame)
        self.entry_autor.pack()

        self.label_ano = tk.Label(self.frame, text="Ano:")
        self.label_ano.pack()
        self.entry_ano = tk.Entry(self.frame)
        self.entry_ano.pack()
        

        self.button_cadastrar = tk.Button(self.frame, text="Cadastrar", command=self.cadastrar)
        self.button_cadastrar.pack()

    def cadastrar(self):
        titulo = self.entry_titulo.get()
        autor = self.entry_autor.get()
        ano = self.entry_ano.get()

        # if adicionar_livro(titulo, autor, ano): #Com banco de dados
        if titulo and autor and ano:  # Verificação simples
            messagebox.showinfo("Sucesso", "Livro cadastrado!")
            self.frame.destroy()
        else:
            messagebox.showerror("Erro", "Preencha todos os campos.")